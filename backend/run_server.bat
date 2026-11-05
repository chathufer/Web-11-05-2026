@echo off
title Media Downloader Pro — License Server Backend
cd /d "%~dp0"
echo ==========================================================
echo    Media Downloader Pro — License Server
echo ==========================================================
echo Server running at: http://localhost:5000
echo Admin Dashboard:   http://localhost:5000/admin
echo Admin API Key:     MDP_ADMIN_SECRET_KEY_2026
echo ==========================================================
python server.py
pause
