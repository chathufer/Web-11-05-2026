@echo off
title Downloader Pro — Public Cloud Storefront & License Server
cd /d "%~dp0"
echo ======================================================================
echo    DOWNLOADER PRO — PUBLIC CLOUD STOREFRONT & SERVER (FREE TUNNEL)
echo ======================================================================
echo.
echo 1. Starting local Flask server on port 5000...
start "Downloader Pro - Server Backend" /min python backend/server.py
timeout /t 2 >nul
echo.
echo 2. Establishing secure public HTTPS tunnel via localhost.run...
echo.
echo ======================================================================
echo YOUR PUBLIC WEBSITE & LICENSE SERVER URL WILL APPEAR BELOW:
echo Customers worldwide can visit this URL to buy licenses & download the app.
echo ======================================================================
echo.
ssh -o StrictHostKeyChecking=no -R 80:localhost:5000 nokey@localhost.run
pause
