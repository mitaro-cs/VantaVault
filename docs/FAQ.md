# FAQ

## Is VantaVault cloud-based?

No. The product is designed as a local-first desktop vault for removable drives.

## Does it upload my files anywhere?

No. The application does not send vault data to an external service.

## What is the main use case?

Keeping an external disk in a predictable desktop workflow:

- detect the right disk
- unlock the app locally
- browse the drive
- create local AES archives when needed

## Does it support macOS and Windows?

Yes.

- `macOS` releases are shipped as `dmg`
- `Windows` releases are shipped as `exe`

## Can I run it from source instead of downloading a release?

Yes. Use the repository bootstrap launchers:

- `./main`
- `.\main.ps1`
- `main.bat`

## Is there destructive auto-wipe after failed logins?

No. The current design uses safe temporary lockout, not destructive auto-deletion.

## What is used for archive encryption?

AES archives are handled locally through `pyzipper`.

## Where should I report bugs or ask for help?

- bugs: GitHub Issues
- feature ideas: GitHub Issues
- support and routing: [../SUPPORT.md](../SUPPORT.md)
- vulnerabilities: [../SECURITY.md](../SECURITY.md)
