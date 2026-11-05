@echo off
title Build Commercial Single-File Setup Installer
cd /d "%~dp0"
echo ==========================================================
echo    Building Media Downloader Pro Setup Installer (.exe)
echo ==========================================================
python build_setup.py
echo.
pause
