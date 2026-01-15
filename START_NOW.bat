@echo off
echo ============================================
echo   AniGen - Ultra Simple Version
echo ============================================
echo.

echo Installing ONE dependency...
python -m pip install aiosqlite

echo.
echo Starting system...
python ultra_simple.py

pause
