# Changelog

## 0.2.0

- Added preferred-disk tracking with auto-open and missing-disk notifications.
- Added settings panel for default disk, lockout, and archive parameters.
- Added AES archive create/extract flows with `pyzipper`.
- Added safe lockout mode after repeated wrong passwords.
- Refreshed the UI for disk status, security, and recovery actions.

## 0.1.0

- Initial VantaVault desktop release.
- Local password protection with PBKDF2 hashing.
- Volume scanning and secure local browsing.
- Native desktop shell via `pywebview`.
- macOS packaging to `.app` and `.dmg`.
- Windows `.exe` build pipeline via GitHub Actions.
