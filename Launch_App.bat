@echo off
title YouTube Downloader
cd /d "%~dp0"

if exist "dist\YouTubeDownloader\YouTubeDownloader.exe" (
    start "" "dist\YouTubeDownloader\YouTubeDownloader.exe"
) else (
    start "" pythonw main.py
)
exit
