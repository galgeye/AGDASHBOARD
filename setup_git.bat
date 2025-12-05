@echo off
echo Checking for Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

echo Initializing Git Repository...
git init

echo Adding files...
git add .

echo Committing files...
git commit -m "Initial commit: Technical specification and dashboard prototype"

echo.
echo ========================================================
echo Repository initialized and files committed!
echo.
echo To push to GitHub, run the following commands:
echo.
echo   git branch -M main
echo   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
echo   git push -u origin main
echo.
echo ========================================================
pause


