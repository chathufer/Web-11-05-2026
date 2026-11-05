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

echo [1/4] Verifying Git environment...
git --version
if errorlevel 1 (
    echo [ERROR] Git could not be initialized from %GIT_DIR%.
    pause
    exit /b
)

echo.
echo [2/4] Staging and committing latest Campus website updates...
git add -A
git commit -m "Update Downloader Pro website to Campus design system" --allow-empty

echo.
echo [3/4] Checking repository destination...
git remote -v

echo.
echo [4/4] Pushing changes to GitHub main branch...
echo (If prompted, confirm your GitHub login or provide your personal access token)
echo.

git push -u origin main

if errorlevel 1 (
    echo.
    echo ===============================================================
    echo [NOTE] Push failed. If you were prompted for credentials:
    echo        Username: chathufer
    echo        Password: Your GitHub Personal Access Token (PAT)
    echo ===============================================================
) else (
    echo.
    echo ===============================================================
    echo   [SUCCESS] Code successfully pushed to GitHub!
    echo   Vercel is now automatically building and deploying!
    echo.
    echo   Check your live site on Vercel:
    echo   https://prodownloader.site
    echo   or your *.vercel.app deployment URL in your Vercel Dashboard
    echo ===============================================================
)

echo.
pause
