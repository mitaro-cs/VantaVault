# Getting Started

There are two normal ways to use `VantaVault`:

1. download a ready-made release
2. run the project directly from source

## Option 1. Download a Release

Open:

- `https://github.com/mitaro-cs/VantaVault/releases/latest`

Choose the file for your platform:

- `VantaVault-vX.Y.Z-macos.dmg`
- `VantaVault-vX.Y.Z-windows-x64.exe`

Optional:

- verify the file with the matching `SHA256` asset

## Option 2. Run From Source

### macOS / Linux

```bash
git clone https://github.com/mitaro-cs/VantaVault.git
cd VantaVault
chmod +x main
./main
```

### Windows PowerShell

```powershell
git clone https://github.com/mitaro-cs/VantaVault.git
cd VantaVault
.\main.ps1
```

### Windows double click

- open `main.bat`

## What the bootstrap script does

On the first run it:

- creates a local `.venv`
- installs dependencies from `requirements-desktop.txt`
- launches the app

On later runs it:

- reuses the existing environment
- reinstalls dependencies only when `requirements-desktop.txt` changes

## Install without launching

### macOS / Linux

```bash
./main --install-only
```

### Windows

```powershell
.\main.ps1 --install-only
```

## First Launch

When `VantaVault` opens for the first time:

- set a local password
- choose your preferred removable drive
- open the settings if you want default behavior
- start working inside the vault

If the desktop shell is unavailable, the app falls back to the local browser version automatically.
