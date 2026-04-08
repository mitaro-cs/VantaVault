# Troubleshooting

## Python is not found

Symptoms:

- `python` or `python3` is missing
- `main.ps1` or `main.bat` exits immediately

Fix:

- install Python 3
- on Windows, enable the option to add Python to `PATH`
- run the bootstrap script again

## `.venv` cannot be created

Symptoms:

- bootstrap fails during `python -m venv`
- no local environment is created

Fix:

- make sure the standard `venv` module is available
- on Linux you may need a package such as `python3-venv`
- run `./main --install-only` or `.\main.ps1 --install-only` again

## The app opens in a browser instead of a native window

This means the local backend started but the desktop shell was not available at runtime.

What to do:

- rerun bootstrap and confirm dependencies installed correctly
- check `requirements-desktop.txt`
- use the browser fallback if the native shell is unavailable on the machine

## The preferred drive is not detected

Check:

- the drive is physically connected
- the volume is mounted by the OS
- the correct target disk is selected in settings
- the app has been refreshed after the drive appeared

## macOS warns before opening the app

This can happen with a new or unsigned local build.

Typical fixes:

- open the app from the context menu and choose `Open`
- confirm the system dialog
- allow the app in `Privacy & Security` if needed

## Windows SmartScreen shows a warning

This is common for a new or locally built `.exe`.

What to do:

- download only from official GitHub Releases
- verify the file with the provided checksum if needed
- if you trust the source, use `More info` and then `Run anyway`

## Need more help

- quick start: [GETTING_STARTED.md](GETTING_STARTED.md)
- FAQ: [FAQ.md](FAQ.md)
- support routes: [../SUPPORT.md](../SUPPORT.md)
- security reports: [../SECURITY.md](../SECURITY.md)
