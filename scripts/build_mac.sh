#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="$ROOT/.venv-build"

"$PYTHON_BIN" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r "$ROOT/requirements-desktop.txt" -r "$ROOT/requirements-build.txt"
python "$ROOT/scripts/generate_icons.py"

rm -rf "$ROOT/build" "$ROOT/dist" "$ROOT/release/mac-dmg" "$ROOT/release/VantaVault-mac.dmg"

pyinstaller \
  --noconfirm \
  --windowed \
  --name "VantaVault" \
  --icon "$ROOT/assets/generated/vantavault.icns" \
  --add-data "$ROOT/web:web" \
  --collect-all webview \
  "$ROOT/desktop.py"

rm -f "$ROOT/VantaVault.spec"

mkdir -p "$ROOT/release/mac-dmg"
cp -R "$ROOT/dist/VantaVault.app" "$ROOT/release/mac-dmg/VantaVault.app"
ln -s /Applications "$ROOT/release/mac-dmg/Applications"

hdiutil create \
  -volname "VantaVault" \
  -srcfolder "$ROOT/release/mac-dmg" \
  -ov \
  -format UDZO \
  "$ROOT/release/VantaVault-mac.dmg"

echo "Built $ROOT/release/VantaVault-mac.dmg"
