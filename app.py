from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from string import ascii_uppercase
from typing import Any, Iterable
from urllib.parse import parse_qs, urlparse


SOURCE_DIR = Path(__file__).resolve().parent
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", SOURCE_DIR))
WEB_DIR = BUNDLE_DIR / "web"
WEB_ROOT = WEB_DIR.resolve()
VOLUMES_DIR = Path("/Volumes")
SESSION_COOKIE = "vantavault_session"
SESSION_TTL_SECONDS = 60 * 60 * 12
PBKDF2_ROUNDS = 200_000
MAX_DIRECTORY_ITEMS = 500
ENCRYPTED_ARCHIVE_SUFFIX = ".vvault.zip"
DEFAULT_PREFERRED_VOLUME_NAME = "VantaVault"
DEFAULT_SETTINGS: dict[str, Any] = {
    "preferred_volume_id": "",
    "preferred_volume_name": DEFAULT_PREFERRED_VOLUME_NAME,
    "auto_open_preferred": True,
    "notify_missing_preferred": True,
    "open_in_file_manager_on_connect": False,
    "failed_attempt_limit": 5,
    "lockout_seconds": 900,
    "encryption_default_name": "vault-backup",
}

RUNTIME_SECRET = secrets.token_bytes(32)
STATE_LOCK = threading.Lock()


def get_user_data_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "VantaVault"
    if os.name == "nt":
        appdata = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
        if appdata:
            return Path(appdata) / "VantaVault"
        return Path.home() / "AppData" / "Roaming" / "VantaVault"
    data_home = os.environ.get("XDG_DATA_HOME")
    if data_home:
        return Path(data_home) / "VantaVault"
    return Path.home() / ".local" / "share" / "VantaVault"


DATA_DIR = get_user_data_dir()
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / "state.json"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return now_utc().isoformat()


def parse_iso_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_bytes(value: int | float | None) -> str:
    if value is None:
        return "-"
    size = float(value)
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{int(value)} B"


def get_disk_usage(path: Path) -> tuple[int, int, int]:
    try:
        usage = shutil.disk_usage(path)
    except OSError:
        return 0, 0, 0
    total_bytes = int(usage.total)
    free_bytes = int(usage.free)
    used_bytes = max(0, total_bytes - free_bytes)
    return total_bytes, free_bytes, used_bytes


def make_default_state() -> dict[str, Any]:
    return {
        "password_hash": "",
        "password_salt": "",
        "last_volume": "",
        "failed_attempts": 0,
        "lockout_until": "",
        "settings": dict(DEFAULT_SETTINGS),
    }


def clamp_int(
    value: Any,
    *,
    default: int,
    min_value: int,
    max_value: int,
) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(min_value, min(max_value, number))


def coerce_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def safe_text(value: Any, *, default: str = "", max_length: int = 240) -> str:
    text = str(value or "").strip()
    if not text:
        return default
    return text[:max_length]


def sanitize_component_name(value: str, default: str, *, max_length: int = 120) -> str:
    cleaned = safe_text(value, default="", max_length=max_length)
    cleaned = cleaned.replace("\\", "/").split("/")[-1]
    for char in '<>:"|?*':
        cleaned = cleaned.replace(char, "-")
    cleaned = cleaned.strip(" .")
    return cleaned or default


def sanitize_archive_name(value: str, default: str = "vault-backup") -> str:
    cleaned = sanitize_component_name(value, default)
    if not cleaned.lower().endswith(".zip"):
        cleaned = f"{cleaned}{ENCRYPTED_ARCHIVE_SUFFIX}"
    return cleaned


def sanitize_output_folder_name(value: str, default: str = "restored") -> str:
    return sanitize_component_name(value, default)


def normalize_settings(data: Any) -> dict[str, Any]:
    raw = data if isinstance(data, dict) else {}
    preferred_volume_id = safe_text(raw.get("preferred_volume_id", ""), default="", max_length=320)
    preferred_volume_name = safe_text(
        raw.get("preferred_volume_name", DEFAULT_PREFERRED_VOLUME_NAME),
        default=DEFAULT_PREFERRED_VOLUME_NAME,
        max_length=120,
    )
    encryption_default_name = sanitize_component_name(
        str(raw.get("encryption_default_name", DEFAULT_SETTINGS["encryption_default_name"])),
        str(DEFAULT_SETTINGS["encryption_default_name"]),
    )
    return {
        "preferred_volume_id": preferred_volume_id,
        "preferred_volume_name": preferred_volume_name,
        "auto_open_preferred": coerce_bool(
            raw.get("auto_open_preferred"),
            bool(DEFAULT_SETTINGS["auto_open_preferred"]),
        ),
        "notify_missing_preferred": coerce_bool(
            raw.get("notify_missing_preferred"),
            bool(DEFAULT_SETTINGS["notify_missing_preferred"]),
        ),
        "open_in_file_manager_on_connect": coerce_bool(
            raw.get("open_in_file_manager_on_connect"),
            bool(DEFAULT_SETTINGS["open_in_file_manager_on_connect"]),
        ),
        "failed_attempt_limit": clamp_int(
            raw.get("failed_attempt_limit"),
            default=int(DEFAULT_SETTINGS["failed_attempt_limit"]),
            min_value=3,
            max_value=10,
        ),
        "lockout_seconds": clamp_int(
            raw.get("lockout_seconds"),
            default=int(DEFAULT_SETTINGS["lockout_seconds"]),
            min_value=60,
            max_value=86_400,
        ),
        "encryption_default_name": encryption_default_name,
    }


def normalize_state(data: Any) -> dict[str, Any]:
    defaults = make_default_state()
    raw = data if isinstance(data, dict) else {}
    normalized = dict(defaults)
    normalized["password_hash"] = safe_text(raw.get("password_hash", ""), default="", max_length=1024)
    normalized["password_salt"] = safe_text(raw.get("password_salt", ""), default="", max_length=1024)
    normalized["last_volume"] = safe_text(raw.get("last_volume", ""), default="", max_length=320)
    normalized["failed_attempts"] = clamp_int(
        raw.get("failed_attempts"),
        default=0,
        min_value=0,
        max_value=99,
    )
    lockout_until = safe_text(raw.get("lockout_until", ""), default="", max_length=128)
    normalized["lockout_until"] = lockout_until if parse_iso_datetime(lockout_until) else ""
    normalized["settings"] = normalize_settings(raw.get("settings"))
    return normalized


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return make_default_state()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return make_default_state()
    return normalize_state(data)


def save_state(state: dict[str, Any]) -> None:
    normalized = normalize_state(state)
    STATE_FILE.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def hash_password(password: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ROUNDS,
    )
    return base64.b64encode(digest).decode("ascii")


def create_password_record(password: str) -> tuple[str, str]:
    salt = secrets.token_bytes(16)
    return hash_password(password, salt), base64.b64encode(salt).decode("ascii")


def verify_password(password: str, state: dict[str, Any]) -> bool:
    password_hash = state.get("password_hash", "")
    salt_encoded = state.get("password_salt", "")
    if not password_hash or not salt_encoded:
        return False
    try:
        salt = base64.b64decode(salt_encoded.encode("ascii"))
    except Exception:
        return False
    candidate = hash_password(password, salt)
    return hmac.compare_digest(candidate, password_hash)


def encode_session_token() -> str:
    payload = {
        "kind": "auth",
        "ts": int(time.time()),
        "nonce": secrets.token_hex(8),
    }
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    signature = hmac.new(
        RUNTIME_SECRET,
        payload_b64.encode("ascii"),
        hashlib.sha256,
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"{payload_b64}.{sig_b64}"


def decode_session_token(token: str) -> bool:
    try:
        payload_b64, sig_b64 = token.split(".", 1)
    except ValueError:
        return False

    expected_sig = hmac.new(
        RUNTIME_SECRET,
        payload_b64.encode("ascii"),
        hashlib.sha256,
    ).digest()
    try:
        received_sig = base64.urlsafe_b64decode(sig_b64 + "=" * (-len(sig_b64) % 4))
    except Exception:
        return False
    if not hmac.compare_digest(expected_sig, received_sig):
        return False

    try:
        raw = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4))
        payload = json.loads(raw.decode("utf-8"))
    except Exception:
        return False

    if payload.get("kind") != "auth":
        return False

    issued_at = int(payload.get("ts", 0))
    return (int(time.time()) - issued_at) <= SESSION_TTL_SECONDS


def clear_expired_lockout(state: dict[str, Any]) -> bool:
    raw_value = str(state.get("lockout_until", ""))
    if not raw_value:
        return False
    lockout_until = parse_iso_datetime(raw_value)
    if lockout_until is None:
        state["lockout_until"] = ""
        state["failed_attempts"] = 0
        return True
    if lockout_until <= now_utc():
        state["lockout_until"] = ""
        state["failed_attempts"] = 0
        return True
    return False


def get_lockout_remaining_seconds(state: dict[str, Any]) -> int:
    lockout_until = parse_iso_datetime(str(state.get("lockout_until", "")))
    if lockout_until is None:
        return 0
    remaining = int((lockout_until - now_utc()).total_seconds())
    return max(0, remaining)


def reset_failed_attempts(state: dict[str, Any]) -> None:
    state["failed_attempts"] = 0
    state["lockout_until"] = ""


def record_failed_attempt(state: dict[str, Any]) -> tuple[int, int]:
    clear_expired_lockout(state)
    settings = normalize_settings(state.get("settings"))
    state["settings"] = settings
    attempts = clamp_int(state.get("failed_attempts"), default=0, min_value=0, max_value=99) + 1
    state["failed_attempts"] = attempts
    remaining = 0
    if attempts >= settings["failed_attempt_limit"]:
        state["lockout_until"] = (now_utc() + timedelta(seconds=settings["lockout_seconds"])).isoformat()
        remaining = settings["lockout_seconds"]
    return attempts, remaining


def get_preferred_volume_label(settings: dict[str, Any]) -> str:
    preferred_name = safe_text(settings.get("preferred_volume_name", ""), default="", max_length=120)
    if preferred_name:
        return preferred_name
    preferred_id = safe_text(settings.get("preferred_volume_id", ""), default="", max_length=320)
    if preferred_id:
        return Path(preferred_id).name or preferred_id
    return DEFAULT_PREFERRED_VOLUME_NAME


def find_preferred_volume(
    volumes: list[dict[str, Any]],
    settings: dict[str, Any],
) -> dict[str, Any] | None:
    preferred_id = str(settings.get("preferred_volume_id", "")).strip()
    if preferred_id:
        for volume in volumes:
            if str(volume.get("id", "")) == preferred_id:
                return volume
    preferred_name = str(settings.get("preferred_volume_name", "")).strip().lower()
    if preferred_name:
        for volume in volumes:
            if str(volume.get("name", "")).strip().lower() == preferred_name:
                return volume
    return None


def snapshot_state_locked() -> tuple[dict[str, Any], bool]:
    normalized = normalize_state(APP_CONTEXT.state)
    changed = APP_CONTEXT.state != normalized
    APP_CONTEXT.state = normalized
    if clear_expired_lockout(APP_CONTEXT.state):
        changed = True
    if changed:
        save_state(APP_CONTEXT.state)
    return normalize_state(APP_CONTEXT.state), changed


def build_status_payload_from_state(
    state_snapshot: dict[str, Any],
    *,
    authenticated: bool,
    include_volumes: bool = False,
    volumes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if volumes is None:
        volumes = list_volumes()
    settings = normalize_settings(state_snapshot.get("settings"))
    preferred = find_preferred_volume(volumes, settings)
    payload: dict[str, Any] = {
        "ok": True,
        "configured": bool(state_snapshot.get("password_hash")),
        "authenticated": authenticated,
        "last_volume": str(state_snapshot.get("last_volume", "")),
        "failed_attempts": clamp_int(
            state_snapshot.get("failed_attempts"),
            default=0,
            min_value=0,
            max_value=99,
        ),
        "failed_attempt_limit": int(settings["failed_attempt_limit"]),
        "lockout_remaining_seconds": get_lockout_remaining_seconds(state_snapshot),
        "preferred_volume_name": get_preferred_volume_label(settings),
        "preferred_volume_connected": preferred is not None,
        "preferred_volume": preferred,
        "settings": settings,
    }
    if include_volumes:
        payload["volumes"] = volumes
    return payload


def build_status_payload(*, authenticated: bool, include_volumes: bool = False) -> dict[str, Any]:
    volumes = list_volumes()
    with STATE_LOCK:
        snapshot, _ = snapshot_state_locked()
    return build_status_payload_from_state(
        snapshot,
        authenticated=authenticated,
        include_volumes=include_volumes,
        volumes=volumes,
    )


def get_real_volume_root(volume_id: str) -> Path:
    if not volume_id:
        raise ValueError("Не выбран диск.")

    known_volumes = {item["id"]: Path(item["path"]) for item in list_volumes()}
    raw_path = known_volumes.get(volume_id)
    if raw_path is None:
        raise FileNotFoundError("Диск не найден.")
    if not raw_path.exists() or not raw_path.is_dir():
        raise FileNotFoundError("Диск не найден.")
    return raw_path


def get_safe_target(volume_id: str, relative_path: str = "") -> tuple[Path, Path]:
    volume_root = get_real_volume_root(volume_id).resolve()
    target = (volume_root / relative_path).resolve()
    try:
        target.relative_to(volume_root)
    except ValueError as exc:
        raise PermissionError("Некорректный путь.") from exc
    return volume_root, target


def resolve_web_asset_path(request_path: str) -> Path:
    if not request_path.startswith("/assets/"):
        raise ValueError("Некорректный путь к ресурсу.")
    target = (WEB_DIR / request_path.removeprefix("/assets/")).resolve()
    try:
        target.relative_to(WEB_ROOT)
    except ValueError as exc:
        raise PermissionError("Некорректный путь.") from exc
    return target


def list_windows_volumes() -> list[dict[str, Any]]:
    import ctypes

    volumes: list[dict[str, Any]] = []
    kernel32 = ctypes.windll.kernel32
    bitmask = kernel32.GetLogicalDrives()

    for index, letter in enumerate(ascii_uppercase):
        if not (bitmask & (1 << index)):
            continue
        root = Path(f"{letter}:/")
        drive_type = kernel32.GetDriveTypeW(f"{letter}:\\")
        if drive_type not in (2, 3):
            continue

        label_buffer = ctypes.create_unicode_buffer(261)
        filesystem_buffer = ctypes.create_unicode_buffer(261)
        serial = ctypes.c_uint(0)
        component_length = ctypes.c_uint(0)
        flags = ctypes.c_uint(0)

        kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(f"{letter}:\\"),
            label_buffer,
            len(label_buffer),
            ctypes.byref(serial),
            ctypes.byref(component_length),
            ctypes.byref(flags),
            filesystem_buffer,
            len(filesystem_buffer),
        )

        total_bytes, free_bytes, used_bytes = get_disk_usage(root)
        label = label_buffer.value.strip() or f"{letter}:"
        volumes.append(
            {
                "id": f"{letter}:/",
                "name": label,
                "path": str(root),
                "used_bytes": used_bytes,
                "free_bytes": free_bytes,
                "total_bytes": total_bytes,
                "used_label": format_bytes(used_bytes),
                "free_label": format_bytes(free_bytes),
                "total_label": format_bytes(total_bytes),
                "kind": "removable" if drive_type == 2 else "disk",
            }
        )

    return volumes


def list_macos_volumes() -> list[dict[str, Any]]:
    volumes: list[dict[str, Any]] = []
    if not VOLUMES_DIR.exists():
        return volumes

    for child in sorted(VOLUMES_DIR.iterdir(), key=lambda item: item.name.lower()):
        if child.name.startswith("."):
            continue
        if not child.is_dir():
            continue
        if not os.path.ismount(child):
            continue
        total_bytes, free_bytes, used_bytes = get_disk_usage(child)
        volumes.append(
            {
                "id": str(child),
                "name": child.name,
                "path": str(child),
                "used_bytes": used_bytes,
                "free_bytes": free_bytes,
                "total_bytes": total_bytes,
                "used_label": format_bytes(used_bytes),
                "free_label": format_bytes(free_bytes),
                "total_label": format_bytes(total_bytes),
                "kind": "volume",
            }
        )
    return volumes


def list_volumes() -> list[dict[str, Any]]:
    if os.name == "nt":
        return list_windows_volumes()
    return list_macos_volumes()


def list_directory(volume_id: str, relative_path: str = "") -> dict[str, Any]:
    volume_root, target = get_safe_target(volume_id, relative_path)
    if not target.exists():
        raise FileNotFoundError("Папка не найдена.")
    if not target.is_dir():
        raise NotADirectoryError("Указанный путь не является папкой.")

    entries: list[dict[str, Any]] = []
    try:
        children = [
            child
            for child in sorted(
                target.iterdir(),
                key=lambda item: (not item.is_dir(), item.name.lower()),
            )
            if not child.name.startswith(".")
        ]
    except OSError as exc:
        raise PermissionError("Не удалось открыть папку.") from exc
    for child in children[:MAX_DIRECTORY_ITEMS]:
        try:
            stat = child.stat()
        except OSError:
            continue
        relative_child = str(child.relative_to(volume_root))
        entry = {
            "name": child.name,
            "relative_path": relative_child,
            "is_dir": child.is_dir(),
            "is_archive": child.is_file() and child.suffix.lower() == ".zip",
            "size_bytes": None if child.is_dir() else stat.st_size,
            "size_label": None if child.is_dir() else format_bytes(stat.st_size),
            "modified_at": datetime.fromtimestamp(
                stat.st_mtime,
                tz=timezone.utc,
            ).astimezone().isoformat(),
            "extension": child.suffix.lower(),
        }
        entries.append(entry)

    current_relative = ""
    if target != volume_root:
        current_relative = str(target.relative_to(volume_root))

    breadcrumbs = [{"label": volume_root.name, "relative_path": ""}]
    if current_relative:
        parts = current_relative.split(os.sep)
        current = []
        for part in parts:
            current.append(part)
            breadcrumbs.append(
                {"label": part, "relative_path": "/".join(current)},
            )

    parent_relative = ""
    if target != volume_root:
        parent_relative = str(target.parent.relative_to(volume_root))
        if parent_relative == ".":
            parent_relative = ""

    return {
        "volume_id": str(volume_root),
        "volume_name": volume_root.name,
        "current_path": current_relative,
        "display_path": "/" if not current_relative else f"/{current_relative}",
        "parent_path": parent_relative,
        "breadcrumbs": breadcrumbs,
        "items": entries,
    }


def open_in_file_manager(volume_id: str, relative_path: str = "") -> None:
    _, target = get_safe_target(volume_id, relative_path)
    if not target.exists():
        raise FileNotFoundError("Объект не найден.")
    if os.name == "nt":
        os.startfile(str(target))
        return
    subprocess.run(["open", str(target)], check=False)


def load_pyzipper_module() -> Any:
    try:
        import pyzipper
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "AES-архивирование недоступно: установи зависимость `pyzipper`."
        ) from exc
    return pyzipper


def default_archive_name_for_target(
    source: Path,
    fallback_name: str,
) -> str:
    if source.name:
        base = source.stem if source.is_file() and source.suffix else source.name
    else:
        base = fallback_name
    return sanitize_archive_name(base, fallback_name)


def default_output_name_for_archive(archive_path: Path) -> str:
    name = archive_path.name
    lowered = name.lower()
    if lowered.endswith(ENCRYPTED_ARCHIVE_SUFFIX):
        base = name[: -len(ENCRYPTED_ARCHIVE_SUFFIX)]
    elif archive_path.suffix.lower() == ".zip":
        base = archive_path.stem
    else:
        base = archive_path.name
    return sanitize_output_folder_name(f"{base}-restored", "restored")


def iter_archive_members(
    source: Path,
    archive_path: Path,
) -> Iterable[tuple[Path | None, str]]:
    if source.is_file():
        yield source, source.name
        return

    archive_resolved = archive_path.resolve()
    for current_root, dirnames, filenames in os.walk(source):
        dirnames.sort()
        filenames.sort()
        current_path = Path(current_root)
        relative_dir = current_path.relative_to(source)

        if not dirnames and not filenames:
            if relative_dir != Path("."):
                yield None, relative_dir.as_posix()
            continue

        for filename in filenames:
            file_path = current_path / filename
            if file_path.resolve() == archive_resolved:
                continue
            if relative_dir == Path("."):
                arcname = Path(filename).as_posix()
            else:
                arcname = (relative_dir / filename).as_posix()
            yield file_path, arcname


def create_encrypted_archive(
    volume_id: str,
    relative_path: str,
    password: str,
    archive_name: str,
) -> dict[str, Any]:
    if len(password) < 4:
        raise ValueError("Пароль архива должен быть не короче 4 символов.")

    pyzipper = load_pyzipper_module()
    volume_root, source = get_safe_target(volume_id, relative_path)
    if not source.exists():
        raise FileNotFoundError("Объект для шифрования не найден.")

    with STATE_LOCK:
        snapshot, _ = snapshot_state_locked()
    fallback_name = str(snapshot["settings"]["encryption_default_name"])

    archive_file_name = sanitize_archive_name(
        archive_name or default_archive_name_for_target(source, fallback_name),
        fallback_name,
    )
    output_dir = source.parent if source != volume_root else volume_root
    archive_path = (output_dir / archive_file_name).resolve()
    try:
        archive_path.relative_to(volume_root)
    except ValueError as exc:
        raise PermissionError("Некорректный путь к архиву.") from exc
    if archive_path.exists():
        raise FileExistsError("Архив с таким именем уже существует.")

    try:
        with pyzipper.AESZipFile(
            archive_path,
            "w",
            compression=pyzipper.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES,
        ) as archive:
            archive.setpassword(password.encode("utf-8"))
            archive.setencryption(pyzipper.WZ_AES, nbits=256)
            wrote_any = False
            for member_path, arcname in iter_archive_members(source, archive_path):
                if member_path is None:
                    archive.writestr(f"{arcname}/", b"")
                else:
                    archive.write(member_path, arcname)
                wrote_any = True
            if not wrote_any and source.is_dir():
                archive.writestr("EMPTY.txt", "Пустая папка")
    except OSError as exc:
        if archive_path.exists():
            archive_path.unlink(missing_ok=True)
        raise PermissionError("Не удалось создать архив.") from exc

    size_bytes = archive_path.stat().st_size if archive_path.exists() else 0
    return {
        "path": str(archive_path),
        "relative_path": str(archive_path.relative_to(volume_root)),
        "size_bytes": size_bytes,
        "size_label": format_bytes(size_bytes),
        "name": archive_path.name,
    }


def resolve_extract_target(output_dir: Path, member_name: str) -> Path:
    pure_path = PurePosixPath(member_name)
    if pure_path.is_absolute() or ".." in pure_path.parts:
        raise PermissionError("Архив содержит небезопасные пути.")
    target = (output_dir / Path(*pure_path.parts)).resolve()
    try:
        target.relative_to(output_dir)
    except ValueError as exc:
        raise PermissionError("Архив содержит небезопасные пути.") from exc
    return target


def extract_encrypted_archive(
    volume_id: str,
    relative_path: str,
    password: str,
    output_name: str,
) -> dict[str, Any]:
    if not password:
        raise ValueError("Введите пароль архива.")

    pyzipper = load_pyzipper_module()
    volume_root, archive_path = get_safe_target(volume_id, relative_path)
    if not archive_path.exists() or not archive_path.is_file():
        raise FileNotFoundError("Архив не найден.")

    default_output_name = default_output_name_for_archive(archive_path)
    output_dir_name = sanitize_output_folder_name(output_name or default_output_name, default_output_name)
    output_dir = (archive_path.parent / output_dir_name).resolve()
    try:
        output_dir.relative_to(volume_root)
    except ValueError as exc:
        raise PermissionError("Некорректная папка для распаковки.") from exc
    if output_dir.exists():
        raise FileExistsError("Папка для распаковки уже существует.")
    output_dir.mkdir(parents=True, exist_ok=False)

    try:
        with pyzipper.AESZipFile(archive_path) as archive:
            archive.setpassword(password.encode("utf-8"))
            for member in archive.infolist():
                target = resolve_extract_target(output_dir, member.filename)
                is_directory = member.is_dir() or member.filename.endswith("/")
                if is_directory:
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source_stream, target.open("wb") as target_stream:
                    shutil.copyfileobj(source_stream, target_stream)
    except RuntimeError as exc:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise PermissionError("Неверный пароль архива или архив поврежден.") from exc
    except (OSError, PermissionError, ValueError) as exc:
        shutil.rmtree(output_dir, ignore_errors=True)
        if isinstance(exc, PermissionError):
            raise
        raise PermissionError("Не удалось распаковать архив.") from exc

    return {
        "path": str(output_dir),
        "relative_path": str(output_dir.relative_to(volume_root)),
        "name": output_dir.name,
    }


@dataclass
class AppContext:
    state: dict[str, Any]
    vault_password: str | None = None


APP_CONTEXT = AppContext(state=load_state())


class AdeptDiskHandler(BaseHTTPRequestHandler):
    server_version = "VantaVault/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def require_auth(self) -> bool:
        if self.is_authenticated():
            return True
        payload = build_status_payload(authenticated=False)
        payload["ok"] = False
        payload["error"] = "Требуется авторизация."
        self.send_json(payload, status=HTTPStatus.UNAUTHORIZED)
        return False

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.serve_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
            return

        if parsed.path.startswith("/assets/"):
            try:
                asset_path = resolve_web_asset_path(parsed.path)
            except (ValueError, PermissionError) as exc:
                self.send_json(
                    {"ok": False, "error": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            self.serve_file(asset_path)
            return

        if parsed.path == "/api/status":
            self.send_json(
                build_status_payload(authenticated=self.is_authenticated()),
            )
            return

        if parsed.path == "/api/volumes":
            if not self.require_auth():
                return
            self.send_json(
                build_status_payload(authenticated=True, include_volumes=True),
            )
            return

        if parsed.path == "/api/settings":
            if not self.require_auth():
                return
            self.send_json(
                build_status_payload(authenticated=True, include_volumes=True),
            )
            return

        if parsed.path == "/api/browse":
            if not self.require_auth():
                return
            query = parse_qs(parsed.query)
            volume_name = (query.get("volume") or [""])[0]
            relative_path = (query.get("path") or [""])[0]
            try:
                listing = list_directory(volume_name, relative_path)
            except (ValueError, FileNotFoundError, NotADirectoryError, PermissionError) as exc:
                self.send_json(
                    {"ok": False, "error": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            with STATE_LOCK:
                APP_CONTEXT.state["last_volume"] = volume_name
                save_state(APP_CONTEXT.state)
            self.send_json({"ok": True, "listing": listing})
            return

        self.send_json(
            {"ok": False, "error": "Маршрут не найден."},
            status=HTTPStatus.NOT_FOUND,
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        payload = self.read_json()

        if parsed.path == "/api/setup":
            password = str(payload.get("password", ""))
            if len(password) < 4:
                self.send_json(
                    {"ok": False, "error": "Пароль должен быть не короче 4 символов."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            with STATE_LOCK:
                snapshot, _ = snapshot_state_locked()
                if snapshot.get("password_hash"):
                    self.send_json(
                        {"ok": False, "error": "Пароль уже настроен."},
                        status=HTTPStatus.CONFLICT,
                    )
                    return
                password_hash, password_salt = create_password_record(password)
                APP_CONTEXT.state["password_hash"] = password_hash
                APP_CONTEXT.state["password_salt"] = password_salt
                reset_failed_attempts(APP_CONTEXT.state)
                save_state(APP_CONTEXT.state)
                APP_CONTEXT.vault_password = password
                response_snapshot = normalize_state(APP_CONTEXT.state)
            response_payload = build_status_payload_from_state(
                response_snapshot,
                authenticated=True,
            )
            response_payload["message"] = "Пароль сохранен."
            self.send_json(
                response_payload,
                cookies=[self.build_session_cookie()],
            )
            return

        if parsed.path == "/api/login":
            password = str(payload.get("password", ""))
            with STATE_LOCK:
                snapshot, _ = snapshot_state_locked()
                configured = bool(snapshot.get("password_hash"))
                remaining = get_lockout_remaining_seconds(snapshot)
                if remaining > 0:
                    response_snapshot = normalize_state(snapshot)
                elif not configured:
                    response_snapshot = normalize_state(snapshot)
                else:
                    verified = verify_password(password, snapshot)
                    if verified:
                        reset_failed_attempts(APP_CONTEXT.state)
                        save_state(APP_CONTEXT.state)
                        APP_CONTEXT.vault_password = password
                        response_snapshot = normalize_state(APP_CONTEXT.state)
                        response_payload = build_status_payload_from_state(
                            response_snapshot,
                            authenticated=True,
                        )
                        response_payload["message"] = "Вход выполнен."
                        self.send_json(
                            response_payload,
                            cookies=[self.build_session_cookie()],
                        )
                        return
                    attempts, _ = record_failed_attempt(APP_CONTEXT.state)
                    save_state(APP_CONTEXT.state)
                    response_snapshot = normalize_state(APP_CONTEXT.state)
                    attempts_left = max(
                        0,
                        int(response_snapshot["settings"]["failed_attempt_limit"]) - attempts,
                    )
            response_payload = build_status_payload_from_state(
                response_snapshot,
                authenticated=False,
            )
            if not configured:
                response_payload["ok"] = False
                response_payload["error"] = "Сначала создайте пароль."
                self.send_json(response_payload, status=HTTPStatus.BAD_REQUEST)
                return
            if remaining > 0:
                response_payload["ok"] = False
                response_payload["error"] = "Доступ временно заблокирован после серии неверных попыток."
                self.send_json(response_payload, status=HTTPStatus.LOCKED)
                return
            if response_payload["lockout_remaining_seconds"] > 0:
                response_payload["ok"] = False
                response_payload["error"] = "Слишком много неверных попыток. Доступ временно заблокирован."
                self.send_json(response_payload, status=HTTPStatus.LOCKED)
                return
            response_payload["ok"] = False
            response_payload["error"] = f"Неверный пароль. Осталось попыток: {attempts_left}."
            self.send_json(response_payload, status=HTTPStatus.UNAUTHORIZED)
            return

        if parsed.path == "/api/logout":
            APP_CONTEXT.vault_password = None
            self.send_json(
                {"ok": True},
                cookies=[self.build_clear_cookie()],
            )
            return

        if parsed.path == "/api/open":
            if not self.require_auth():
                return
            volume_name = str(payload.get("volume", ""))
            relative_path = str(payload.get("path", ""))
            try:
                open_in_file_manager(volume_name, relative_path)
            except (ValueError, FileNotFoundError, PermissionError) as exc:
                self.send_json(
                    {"ok": False, "error": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            self.send_json(
                {"ok": True, "message": "Открыто в системном файловом менеджере."},
            )
            return

        if parsed.path == "/api/settings":
            if not self.require_auth():
                return
            volumes = list_volumes()
            with STATE_LOCK:
                snapshot, _ = snapshot_state_locked()
                merged_settings = dict(snapshot["settings"])
                for key in DEFAULT_SETTINGS:
                    if key in payload:
                        merged_settings[key] = payload[key]
                normalized_settings = normalize_settings(merged_settings)
                preferred_id = str(normalized_settings["preferred_volume_id"]).strip()
                if preferred_id:
                    matched = next(
                        (volume for volume in volumes if str(volume.get("id", "")) == preferred_id),
                        None,
                    )
                    if matched is not None:
                        normalized_settings["preferred_volume_name"] = str(matched.get("name", ""))
                APP_CONTEXT.state["settings"] = normalized_settings
                save_state(APP_CONTEXT.state)
                response_snapshot = normalize_state(APP_CONTEXT.state)
            self.send_json(
                build_status_payload_from_state(
                    response_snapshot,
                    authenticated=True,
                    include_volumes=True,
                    volumes=volumes,
                ),
            )
            return

        if parsed.path == "/api/encrypt":
            if not self.require_auth():
                return
            volume_name = str(payload.get("volume", ""))
            relative_path = str(payload.get("path", ""))
            archive_name = str(payload.get("archive_name", ""))
            use_vault_password = coerce_bool(payload.get("use_vault_password"), False)
            password = str(payload.get("password", ""))
            if use_vault_password:
                password = APP_CONTEXT.vault_password or ""
                if not password:
                    self.send_json(
                        {
                            "ok": False,
                            "error": "Пароль текущей сессии недоступен. Введите пароль архива вручную.",
                        },
                        status=HTTPStatus.BAD_REQUEST,
                    )
                    return
            try:
                result = create_encrypted_archive(
                    volume_name,
                    relative_path,
                    password,
                    archive_name,
                )
            except (
                ValueError,
                FileNotFoundError,
                PermissionError,
                FileExistsError,
                RuntimeError,
            ) as exc:
                self.send_json(
                    {"ok": False, "error": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            self.send_json(
                {
                    "ok": True,
                    "message": "AES-архив создан.",
                    "archive": result,
                }
            )
            return

        if parsed.path == "/api/decrypt":
            if not self.require_auth():
                return
            volume_name = str(payload.get("volume", ""))
            relative_path = str(payload.get("path", ""))
            password = str(payload.get("password", ""))
            output_name = str(payload.get("output_name", ""))
            try:
                result = extract_encrypted_archive(
                    volume_name,
                    relative_path,
                    password,
                    output_name,
                )
            except (
                ValueError,
                FileNotFoundError,
                PermissionError,
                FileExistsError,
                RuntimeError,
            ) as exc:
                self.send_json(
                    {"ok": False, "error": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            self.send_json(
                {
                    "ok": True,
                    "message": "Архив распакован.",
                    "output": result,
                }
            )
            return

        self.send_json(
            {"ok": False, "error": "Маршрут не найден."},
            status=HTTPStatus.NOT_FOUND,
        )

    def read_json(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def is_authenticated(self) -> bool:
        cookie_header = self.headers.get("Cookie", "")
        if not cookie_header:
            return False
        cookie = SimpleCookie()
        cookie.load(cookie_header)
        morsel = cookie.get(SESSION_COOKIE)
        if morsel is None:
            return False
        return decode_session_token(morsel.value)

    def build_session_cookie(self) -> str:
        token = encode_session_token()
        return (
            f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; "
            f"Max-Age={SESSION_TTL_SECONDS}"
        )

    def build_clear_cookie(self) -> str:
        return f"{SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"

    def serve_file(self, path: Path, content_type: str | None = None) -> None:
        if not path.exists() or not path.is_file():
            self.send_json(
                {"ok": False, "error": "Файл не найден."},
                status=HTTPStatus.NOT_FOUND,
            )
            return
        body = path.read_bytes()
        if content_type is None:
            guessed, _ = mimetypes.guess_type(path.name)
            content_type = guessed or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(
        self,
        payload: dict[str, Any],
        *,
        status: HTTPStatus = HTTPStatus.OK,
        cookies: list[str] | None = None,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if cookies:
            for cookie in cookies:
                self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VantaVault local app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8421)
    parser.add_argument("--open-browser", action="store_true")
    return parser.parse_args()


def find_available_port(host: str = "127.0.0.1") -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def create_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), AdeptDiskHandler)


def build_local_url(host: str, port: int) -> str:
    return f"http://{host}:{port}"


def main() -> None:
    args = parse_args()
    server = create_server(args.host, args.port)
    url = build_local_url(args.host, args.port)
    print(f"VantaVault started at {url}")
    if args.open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
