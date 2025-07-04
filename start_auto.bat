@echo off
echo ========================================
echo LinkedIn Job Hunter - Fully Automated
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

:: Check if required packages are installed
echo [INFO] Checking dependencies...
python -c "import psutil, requests" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing required packages...
    pip install psutil requests
    if errorlevel 1 (
        echo [ERROR] Failed to install required packages
        pause
        exit /b 1
    )
)

:: Run the automated startup script
echo [INFO] Starting automated startup...
python auto_startup.py

:: If we get here, the script has finished
echo.
echo [INFO] Startup script completed
pause 