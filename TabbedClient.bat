@echo off
REM TabbedClient — Windows Indító Script
title TabbedClient
cd /d "%~dp0"

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python desktop\tabbedclient_windows.py %*
    goto :eof
)

REM Fallback Microsoft Edge App Mode
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --app="file:///%~dp0src/index.html" --user-data-dir="%~dp0data/profiles/default" --no-first-run --window-size=1280,840
    goto :eof
)

if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" --app="file:///%~dp0src/index.html" --user-data-dir="%~dp0data/profiles/default" --no-first-run --window-size=1280,840
    goto :eof
)

start "" "%~dp0src\index.html"
