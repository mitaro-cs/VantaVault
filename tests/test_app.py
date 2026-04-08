import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app


class ResolveWebAssetPathTests(unittest.TestCase):
    def test_allows_asset_inside_web_root(self) -> None:
        asset_path = app.resolve_web_asset_path("/assets/app.js")

        self.assertEqual(asset_path, (app.WEB_DIR / "app.js").resolve())

    def test_rejects_parent_traversal(self) -> None:
        with self.assertRaises(PermissionError):
            app.resolve_web_asset_path("/assets/../app.py")


class StateNormalizationTests(unittest.TestCase):
    def test_normalize_state_adds_settings_defaults(self) -> None:
        normalized = app.normalize_state({"password_hash": "hash"})

        self.assertEqual(normalized["password_hash"], "hash")
        self.assertIn("settings", normalized)
        self.assertEqual(
            normalized["settings"]["preferred_volume_name"],
            app.DEFAULT_PREFERRED_VOLUME_NAME,
        )
        self.assertEqual(
            normalized["settings"]["failed_attempt_limit"],
            5,
        )

    def test_record_failed_attempt_enables_lockout(self) -> None:
        state = app.make_default_state()
        state["settings"]["failed_attempt_limit"] = 3
        state["settings"]["lockout_seconds"] = 120

        app.record_failed_attempt(state)
        app.record_failed_attempt(state)
        attempts, remaining = app.record_failed_attempt(state)

        self.assertEqual(attempts, 3)
        self.assertEqual(remaining, 120)
        self.assertGreater(app.get_lockout_remaining_seconds(state), 0)


class ListDirectoryTests(unittest.TestCase):
    def test_hidden_entries_do_not_consume_visible_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            volume_root = Path(tempdir)
            (volume_root / ".hidden-a").write_text("a", encoding="utf-8")
            (volume_root / ".hidden-b").write_text("b", encoding="utf-8")
            (volume_root / "visible.txt").write_text("ok", encoding="utf-8")

            fake_volumes = [{"id": "test-volume", "path": str(volume_root)}]
            with patch("app.list_volumes", return_value=fake_volumes):
                with patch.object(app, "MAX_DIRECTORY_ITEMS", 2):
                    listing = app.list_directory("test-volume")

        self.assertEqual([item["name"] for item in listing["items"]], ["visible.txt"])


@unittest.skipUnless(importlib.util.find_spec("pyzipper"), "pyzipper is not installed")
class EncryptionRoundTripTests(unittest.TestCase):
    def test_encrypt_and_extract_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            volume_root = Path(tempdir)
            docs_dir = volume_root / "docs"
            docs_dir.mkdir()
            (docs_dir / "note.txt").write_text("vanta vault secret", encoding="utf-8")

            fake_volumes = [
                {
                    "id": "test-volume",
                    "path": str(volume_root),
                    "name": "VantaVault",
                    "used_bytes": 0,
                    "free_bytes": 0,
                    "total_bytes": 0,
                    "used_label": "0 B",
                    "free_label": "0 B",
                    "total_label": "0 B",
                    "kind": "volume",
                }
            ]

            original_state = app.APP_CONTEXT.state
            try:
                app.APP_CONTEXT.state = app.make_default_state()
                with patch("app.list_volumes", return_value=fake_volumes):
                    with patch("app.save_state"):
                        archive = app.create_encrypted_archive(
                            "test-volume",
                            "docs",
                            "secret123",
                            "",
                        )
                        extracted = app.extract_encrypted_archive(
                            "test-volume",
                            archive["relative_path"],
                            "secret123",
                            "docs-restored",
                        )
                        restored_note = volume_root / extracted["relative_path"] / "note.txt"
                        self.assertTrue((volume_root / archive["relative_path"]).exists())
                        self.assertEqual(
                            restored_note.read_text(encoding="utf-8"),
                            "vanta vault secret",
                        )
            finally:
                app.APP_CONTEXT.state = original_state


if __name__ == "__main__":
    unittest.main()
