@echo off
title YouTube Video Downloader
cd /d "%~dp0"

echo Launching YouTube Video Downloader...
start "" pythonw main.py

if %ERRORLEVEL% NEQ 0 (
    echo Pythonw not found, trying python...
    python main.py
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo An error occurred while launching the application.
        pause
    )
)
exit
