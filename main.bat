@echo off
setlocal

set "ROOT=%~dp0"
set "BOOTSTRAP=%ROOT%scripts\bootstrap.py"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%BOOTSTRAP%" %*
    exit /b %errorlevel%
)

where python >nul 2>nul
if %errorlevel%==0 (
    python "%BOOTSTRAP%" %*
    exit /b %errorlevel%
)

echo VantaVault requires Python 3. Install Python and run main.bat again. 1>&2
exit /b 1
