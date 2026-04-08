#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv"
REQUIREMENTS_FILE = ROOT / "requirements-desktop.txt"
STAMP_FILE = VENV_DIR / ".requirements.sha256"


def log(message: str) -> None:
    print(f"[VantaVault] {message}", flush=True)


def venv_python_path() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def requirements_hash() -> str:
    return hashlib.sha256(REQUIREMENTS_FILE.read_bytes()).hexdigest()


def run_command(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def ensure_virtualenv() -> Path:
    python_path = venv_python_path()
    if python_path.exists():
        return python_path

    log("Creating local virtual environment in .venv")
    run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
    return python_path


def ensure_requirements_installed(python_path: Path) -> None:
    expected_hash = requirements_hash()
    current_hash = ""
    if STAMP_FILE.exists():
        current_hash = STAMP_FILE.read_text(encoding="utf-8").strip()

    if current_hash == expected_hash:
        log("Desktop dependencies are ready")
        return

    log("Installing desktop dependencies")
    run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
    run_command([str(python_path), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
    STAMP_FILE.write_text(f"{expected_hash}\n", encoding="utf-8")


def launch_app(python_path: Path) -> int:
    log("Starting VantaVault")
    return subprocess.run([str(python_path), str(ROOT / "desktop.py")], cwd=ROOT).returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap VantaVault locally and optionally launch the app."
    )
    parser.add_argument(
        "--install-only",
        action="store_true",
        help="Prepare the local environment without launching the app.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not REQUIREMENTS_FILE.exists():
        print("requirements-desktop.txt not found.", file=sys.stderr)
        return 1

    python_path = ensure_virtualenv()
    ensure_requirements_installed(python_path)

    if args.install_only:
        log("Setup completed")
        return 0

    return launch_app(python_path)


if __name__ == "__main__":
    raise SystemExit(main())
