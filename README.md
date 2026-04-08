<p align="center">
  <img src="assets/github-banner.svg" alt="VantaVault GitHub Banner" width="100%">
</p>

<h1 align="center">VantaVault</h1>

<p align="center">
  <strong>A premium desktop vault for removable drives.</strong><br>
  Quiet local access, preferred disk awareness, and encrypted archive flow in one deliberate workspace.
</p>

<p align="center">
  <a href="https://github.com/mitaro-cs/VantaVault/releases/latest">
    <img alt="Latest Release" src="https://img.shields.io/github/v/release/mitaro-cs/VantaVault?display_name=tag&style=for-the-badge&label=latest%20release&color=F5F5F7&labelColor=111111">
  </a>
  <a href="https://github.com/mitaro-cs/VantaVault/releases/latest">
    <img alt="Download" src="https://img.shields.io/badge/Download-Releases-F5F5F7?style=for-the-badge&labelColor=111111">
  </a>
  <img alt="License" src="https://img.shields.io/badge/License-MIT-F5F5F7?style=for-the-badge&labelColor=111111">
  <img alt="macOS / Windows" src="https://img.shields.io/badge/macOS%20%2F%20Windows-supported-F5F5F7?style=for-the-badge&labelColor=111111">
</p>

<p align="center">
  <a href="#overview">Overview</a> ·
  <a href="#download">Download</a> ·
  <a href="#run-from-source">Run From Source</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="#security">Security</a>
</p>

## Overview

`VantaVault` is built for one very specific job: turning an external drive into a calm,
high-quality desktop workspace.

<table>
  <tr>
    <td width="33.33%" valign="top">
      <h3>Disk-aware</h3>
      <p>Knows when the preferred removable drive is mounted, missing, or ready.</p>
    </td>
    <td width="33.33%" valign="top">
      <h3>Local-first</h3>
      <p>Keeps access behind local authentication and safe lockout without cloud services.</p>
    </td>
    <td width="33.33%" valign="top">
      <h3>Archive-ready</h3>
      <p>Creates and restores local AES archives from the same workspace.</p>
    </td>
  </tr>
</table>

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
- local AES archive creation

See [SECURITY.md](SECURITY.md) for reporting guidance.

## License

Released under the `MIT` license. See [LICENSE](LICENSE).
