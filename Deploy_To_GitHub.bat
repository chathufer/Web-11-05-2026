@echo off
title Deploy Downloader Pro to GitHub and Vercel
cls
color 0b
echo ===============================================================
echo          DEPLOYING DOWNLOADER PRO TO GITHUB & VERCEL
echo ===============================================================
echo.

set "GIT_DIR=C:\Users\Chathufer\AppData\Local\GitHubDesktop\app-3.6.10\resources\app\git\cmd"
set "PATH=%GIT_DIR%;%PATH%"

echo [1/3] Verifying Git environment...
git --version
if errorlevel 1 (
    echo [ERROR] Git could not be initialized.
    pause
    exit /b
)

echo [2/3] Checking repository destination...
git remote -v

echo.
echo [3/3] Pushing luxury storefront & Vercel serverless backend to main branch...
echo (If a browser window appears, simply click "Authorize" to confirm your GitHub login)
echo.

git push -u origin main --force

if errorlevel 1 (
    echo.
    echo [NOTE] If you were prompted for a Personal Access Token:
    echo        Username: chathufer
    echo        Password: Your GitHub Personal Access Token
    echo.
) else (
    echo.
    echo ===============================================================
    echo   [SUCCESS] Code successfully pushed to GitHub!
    echo   Vercel is now building and deploying prodownloader.site!
    echo   Open your browser and refresh: https://prodownloader.site
    echo ===============================================================
)

echo.
pause
