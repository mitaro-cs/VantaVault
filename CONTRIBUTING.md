# Contributing to VantaVault

Thanks for your interest in improving `VantaVault`.

This repository is open to:

- bug fixes
- UX improvements
- documentation updates
- release and packaging improvements
- tests
- well-scoped product features

## Before you start

- for small fixes, a direct PR is fine
- for larger changes, open an issue first so the direction is clear
- for security-sensitive findings, follow [SECURITY.md](SECURITY.md) instead of posting public exploit details

## Local setup

Install and launch:

```bash
./main
```

Or install only:

```bash
./main --install-only
```

## Useful checks

```bash
python3 -m py_compile app.py desktop.py scripts/bootstrap.py tests/test_app.py
python3 -m unittest discover -s tests -v
```

## Pull request guidelines

- keep changes scoped and easy to review
- avoid mixing unrelated refactors, features, and visual tweaks in one PR
- update documentation if behavior changes
- add or update tests when logic changes
- include screenshots for UI changes
- explain how the change was verified

## Good contribution areas

- better drive-detection UX
- archive and recovery workflows
- release and installer polish
- README and public docs
- UI quality and accessibility
- tests around backend behavior

## Communication

- be direct and respectful
- criticize ideas, not people
- keep technical arguments concrete
- use issues and PRs to make decisions easy to follow

Project behavior expectations are defined in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
