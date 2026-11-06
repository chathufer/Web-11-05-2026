@echo off
cd /d "%~dp0"
if exist "dist\YouTubeDownloader\YouTubeDownloader.exe" (
    start "" "dist\YouTubeDownloader\YouTubeDownloader.exe"
    exit /b 0
)
where pythonw >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" pythonw main.py
    exit /b 0
) else (
    start "" python main.py
    exit /b 0
)
