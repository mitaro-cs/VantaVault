# Security Policy

`VantaVault` works with local authentication, removable drives, and encrypted archives, so security reports are treated seriously.

## Supported versions

| Version | Status |
| --- | --- |
| `main` | active |
| latest release | active |
| older releases | best effort |

## Reporting a vulnerability

If you believe you found a vulnerability:

- do not post exploit details in a public issue
- prepare a short description, impact, and reproduction notes
- include the app version, platform, and affected flow
- use a private security reporting route when available

If private reporting is not enabled yet, open a minimal issue without exploit details and request a private contact channel.

## Helpful report details

- where the issue happens
- whether a physical disk is required
- whether it reproduces on a clean setup
- whether it affects authentication, archive handling, or local data access

## What happens next

- the report is reviewed and triaged
- if confirmed, a fix is prepared in `main`
- a release can be published if the issue warrants one
- public disclosure can happen after a fix is available

## Out of scope

Usually not considered critical on their own:

- cosmetic UI issues with no security impact
- dependency notices without a demonstrated impact in this project
- issues that cannot be reproduced on `main` or the latest release
