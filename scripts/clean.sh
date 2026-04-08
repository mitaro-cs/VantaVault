#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

rm -rf "$ROOT/.venv-build"
rm -rf "$ROOT/build"
rm -rf "$ROOT/dist"
rm -rf "$ROOT/release"
rm -rf "$ROOT/assets/generated"
find "$ROOT" -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -f "$ROOT/VantaVault.spec"

echo "Cleaned VantaVault build artifacts."
