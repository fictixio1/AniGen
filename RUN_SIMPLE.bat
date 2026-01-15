@echo off
echo ============================================
echo   AniGen - Simple Setup (No PostgreSQL!)
echo ============================================
echo.

echo [1/2] Installing dependencies...
pip install -r requirements_simple.txt

echo.
echo [2/2] Starting system...
python main_simple.py

pause
