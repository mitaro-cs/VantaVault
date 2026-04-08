$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Bootstrap = Join-Path $Root "scripts\bootstrap.py"

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $Bootstrap @args
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python $Bootstrap @args
    exit $LASTEXITCODE
}

Write-Error "VantaVault requires Python 3. Install Python and run main.ps1 again."
exit 1
