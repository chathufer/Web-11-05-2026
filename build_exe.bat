@echo off
title Build YouTube Downloader Executable
cd /d "%~dp0"

echo Building YouTubeDownloader.exe using PyInstaller...
python build_exe.py

echo.
pause
