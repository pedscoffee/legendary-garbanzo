@echo off
echo ======================================
echo Pediatric Charting Tool Setup
echo ======================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

echo.
echo Installing required packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo To run the application, double-click:
echo   run_app.bat
echo.
echo Or type:
echo   python peds_charting_tool.py
echo.
pause
