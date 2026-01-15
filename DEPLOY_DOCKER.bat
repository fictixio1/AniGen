@echo off
echo ============================================
echo   Deploy AniGen via Docker + Railway CLI
echo ============================================
echo.

cd /d "%~dp0"

echo Running Railway CLI in Docker container...
echo.

docker run -it --rm ^
  -v "%CD%:/app" ^
  -w /app ^
  node:20-alpine sh -c "npm install -g @railway/cli && railway login && railway init && railway add --database postgres && railway variables set GENERATION_MODE=mock SCENES_PER_EPISODE=6 SCENE_GENERATION_INTERVAL_MINUTES=10 LOG_LEVEL=INFO && railway up"

echo.
echo ============================================
echo   Deployment Complete!
echo ============================================
echo.
pause
