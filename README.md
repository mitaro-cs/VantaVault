<p align="center">
  <img src="assets/github-banner.svg" alt="VantaVault GitHub Banner" width="100%">
</p>

<h1 align="center">VantaVault</h1>

<p align="center">
  <strong>A calm desktop vault for removable drives.</strong><br>
  Local access, preferred disk detection, and encrypted archive flow in one clean workspace.
</p>

<p align="center">
  <a href="https://github.com/mitaro-cs/VantaVault/releases/latest">
    <img alt="Latest Release" src="https://img.shields.io/github/v/release/mitaro-cs/VantaVault?display_name=tag&style=for-the-badge&label=latest%20release&color=F5F5F7&labelColor=111111">
  </a>
  <a href="https://github.com/mitaro-cs/VantaVault/releases/latest">
    <img alt="Download" src="https://img.shields.io/badge/Download-Releases-F5F5F7?style=for-the-badge&labelColor=111111">
  </a>
  <img alt="License" src="https://img.shields.io/badge/License-MIT-F5F5F7?style=for-the-badge&labelColor=111111">
</p>

<p align="center">
  <a href="#overview">Overview</a> ·
  <a href="#download">Download</a> ·
  <a href="#run-from-source">Run From Source</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="#security">Security</a>
</p>

## Overview

`VantaVault` is built around one job: making an external drive feel like a polished desktop product.

- detects the preferred removable drive
- keeps access behind local auth and safe lockout
- opens a clear workspace for the right volume
- creates local AES archives without cloud services

## Download

The easiest path is [Latest Release](https://github.com/mitaro-cs/VantaVault/releases/latest).

- `VantaVault-vX.Y.Z-macos.dmg`
- `VantaVault-vX.Y.Z-windows-x64.exe`
- `SHA256` verification files

## Run From Source

### macOS / Linux

```bash
git clone https://github.com/mitaro-cs/VantaVault.git
cd VantaVault
chmod +x main
./main
```

### Windows

```powershell
git clone https://github.com/mitaro-cs/VantaVault.git
cd VantaVault
.\main.ps1
```

Or open `main.bat`.

## Product Flow

<p align="center">
  <img src="assets/github-flow.svg" alt="VantaVault Product Flow" width="100%">
</p>

## Documentation

- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [docs/FAQ.md](docs/FAQ.md)
- [SUPPORT.md](SUPPORT.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

## Security

- local `PBKDF2-SHA256` password storage
- local session protection
- temporary lockout on repeated failures
- no destructive auto-wipe
- local AES archive creation

See [SECURITY.md](SECURITY.md) for reporting guidance.

## License

Released under the `MIT` license. See [LICENSE](LICENSE).
