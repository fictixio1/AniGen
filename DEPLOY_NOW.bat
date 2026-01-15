@echo off
echo ============================================
echo   Deploy AniGen to Railway
echo ============================================
echo.

echo Step 1: Installing Railway CLI...
npm i -g @railway/cli
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Railway CLI
    echo Make sure Node.js is installed: https://nodejs.org
    pause
    exit /b 1
)

echo.
echo Step 2: Logging in to Railway...
railway login

echo.
echo Step 3: Initializing project...
railway init

echo.
echo Step 4: Adding PostgreSQL database...
railway add --database postgres

echo.
echo Step 5: Setting environment variables...
railway variables set GENERATION_MODE=mock
railway variables set SCENES_PER_EPISODE=6
railway variables set SCENE_GENERATION_INTERVAL_MINUTES=10
railway variables set LOG_LEVEL=INFO

echo.
echo Step 6: Deploying to Railway...
railway up

echo.
echo ============================================
echo   Deployment Complete!
echo ============================================
echo.
echo View logs: railway logs
echo Open dashboard: railway open
echo.
pause
