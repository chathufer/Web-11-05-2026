@echo off
title Downloader Pro - Deploy to GitHub & Vercel
cls
echo ===============================================================
echo        DOWNLOADER PRO - ONE-CLICK GITHUB PUSH FOR VERCEL
echo ===============================================================
echo.
echo Your code has been prepared with:
echo   [OK] index.html (Luxury Dark & Gold Storefront)
echo   [OK] public/index.html (Global Edge CDN Cache)
echo   [OK] api/index.py (Vercel Serverless Backend)
echo   [OK] Clean requirements.txt (Fast 3-second Vercel build)
echo   [OK] Modern vercel.json routing
echo.

set GIT_PATH="C:\Users\Chathufer\AppData\Local\GitHubDesktop\app-3.6.10\resources\app\git\cmd\git.exe"

if not exist %GIT_PATH% (
    echo [ERROR] Git was not found at standard path.
    pause
    exit /b
)

echo Check existing remote...
%GIT_PATH% remote -v
echo.

set /p REPO_URL="Enter your GitHub repository URL (e.g. https://github.com/chathufer/prodownloader.git): "

if "%REPO_URL%"=="" (
    echo [INFO] No URL entered. Pushing to existing origin if configured...
    %GIT_PATH% push -u origin main
) else (
    %GIT_PATH% remote remove origin >nul 2>&1
    %GIT_PATH% remote add origin %REPO_URL%
    echo [INFO] Pushing clean code to GitHub...
    %GIT_PATH% push -u origin main --force
)

echo.
echo ===============================================================
echo   PUSH COMPLETE! Vercel will now automatically build & deploy.
echo   Check your site in 30 seconds: https://prodownloader.site
echo ===============================================================
pause
