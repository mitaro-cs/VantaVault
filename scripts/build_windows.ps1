$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { "python" }
$VenvDir = Join-Path $Root ".venv-build"

& $Python -m venv $VenvDir
& (Join-Path $VenvDir "Scripts\python.exe") -m pip install --upgrade pip
& (Join-Path $VenvDir "Scripts\python.exe") -m pip install -r (Join-Path $Root "requirements-desktop.txt") -r (Join-Path $Root "requirements-build.txt")
& (Join-Path $VenvDir "Scripts\python.exe") (Join-Path $Root "scripts\generate_icons.py")

Remove-Item -Recurse -Force (Join-Path $Root "build") -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $Root "dist") -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Join-Path $Root "release") | Out-Null
Remove-Item -Force (Join-Path $Root "release\VantaVault.exe") -ErrorAction SilentlyContinue

& (Join-Path $VenvDir "Scripts\pyinstaller.exe") `
  --noconfirm `
  --windowed `
  --onefile `
  --name "VantaVault" `
  --icon (Join-Path $Root "assets\generated\vantavault.ico") `
  --add-data ((Join-Path $Root "web") + ";web") `
  --collect-all webview `
  (Join-Path $Root "desktop.py")

Remove-Item -Force (Join-Path $Root "VantaVault.spec") -ErrorAction SilentlyContinue

Move-Item (Join-Path $Root "dist\VantaVault.exe") (Join-Path $Root "release\VantaVault.exe") -Force
Write-Output "Built $(Join-Path $Root 'release\VantaVault.exe')"
