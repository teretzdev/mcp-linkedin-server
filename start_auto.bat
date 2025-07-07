@echo off
echo LinkedIn MCP Server - Auto Startup
echo ===================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Trying python3...
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python is not installed or not in PATH
        echo Please install Python from https://python.org/
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo Using Python: %PYTHON_CMD%
echo.

REM Check if the auto-start script exists
if not exist "start_auto.py" (
    echo Error: start_auto.py not found
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

echo Starting LinkedIn MCP Server with auto-port detection...
echo This will:
echo - Check dependencies (Node.js, npm)
echo - Install npm dependencies if needed
echo - Find available ports automatically
echo - Start API Bridge and React frontend
echo - Open browser automatically
echo.

REM Run the Python auto-start script
%PYTHON_CMD% start_auto.py

if errorlevel 1 (
    echo.
    echo Auto-start failed with error code %errorlevel%
    echo Please check the error messages above
    pause
    exit /b 1
) else (
    echo.
    echo Auto-start completed successfully
) 