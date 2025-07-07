@echo off
REM IMPORTANT: Run this script in CMD, not PowerShell!
echo Starting LinkedIn MCP Frontend with Auto-Port Detection...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Trying python3...
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python is not installed or not in PATH
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

REM Check if the auto-start script exists
if not exist "start_frontend_auto.py" (
    echo Error: start_frontend_auto.py not found
    echo Falling back to regular npm start...
    call start_frontend.bat
    exit /b
)

echo Using auto-start script for intelligent port management...
echo This will start only the React frontend with auto-port detection.
echo.

REM Run the Python auto-start script
%PYTHON_CMD% start_frontend_auto.py

if errorlevel 1 (
    echo.
    echo Auto-start script failed. Falling back to regular npm start...
    call start_frontend.bat
) 