@echo off
title Downloader Pro — Website & Licensing Server
cd /d "%~dp0"
echo ======================================================================
echo           DOWNLOADER PRO — STOREFRONT & LICENSE SERVER
echo ======================================================================
echo.
echo [OK] Server is starting on port 5000...
echo.
echo  - Customer Website:      http://localhost:5000/
echo  - Seller Admin Portal:   http://localhost:5000/admin
echo  - Network URL (LAN):     http://192.168.1.98:5000/
echo  - Admin Secret Key:      MDP_ADMIN_SECRET_KEY_2026
echo.
echo ======================================================================
echo Keep this window open to serve the website and license activations.
echo Press Ctrl+C to stop the server anytime.
echo ======================================================================
echo.
python backend/server.py
pause
