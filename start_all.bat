@echo off
REM IMPORTANT: Run this script in CMD, not PowerShell!
setlocal enabledelayedexpansion

echo ========================================
echo LinkedIn Job Hunter - Optimized Startup
echo ========================================
echo.

:: Check for .env file
if not exist ".env" (
    echo [INFO] Creating .env file...
    python create_env.py
    if errorlevel 1 (
        echo [ERROR] Failed to create .env file
        pause
        exit /b 1
    )
    echo.
)

:: Optimized process cleanup - only kill if actually running
echo [INFO] Checking for conflicting processes...

:: Function to check if port is in use
set "ports_to_check=5000 5001 5002"
for %%p in (%ports_to_check%) do (
    netstat -ano | findstr ":%%p" | findstr "LISTENING" >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Port %%p is in use, killing process...
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p" ^| findstr "LISTENING"') do (
            taskkill /PID %%a /F >nul 2>&1
            if !errorlevel! equ 0 (
                echo [SUCCESS] Killed process %%a on port %%p
            ) else (
                echo [WARNING] Could not kill process on port %%p
            )
        )
        :: Wait for port to be released
        timeout /t 2 /nobreak >nul
    ) else (
        echo [INFO] Port %%p is available
    )
)

echo.
echo [INFO] Starting services with optimized configuration...
echo.

:: Enhanced error handling for permission errors
set "PERMISSION_ERROR=0"

:: Function to check for permission error in last command
:check_permission_error
if %errorlevel% neq 0 (
    echo [ERROR] Permission denied or port access error detected.
    echo [HINT] Please run this script as administrator.
    set PERMISSION_ERROR=1
    goto :end
)

:: Pre-flight checks
where python >nul 2>nul || (echo Python is not installed. Please install Python and try again. & exit /b 1)
where node >nul 2>nul || (echo Node.js is not installed. Please install Node.js and try again. & exit /b 1)
python -c "import sqlalchemy" 2>nul || (echo Missing Python module: sqlalchemy. Run 'pip install sqlalchemy' and try again. & exit /b 1)
python -c "import fastmcp" 2>nul || (echo Missing Python module: fastmcp. Run 'pip install fastmcp' and try again. & exit /b 1)
netstat -ano | findstr :8002 >nul && (echo Port 8002 is in use. Please free it and try again. & exit /b 1)
netstat -ano | findstr :3000 >nul && (echo Port 3000 is in use. Please free it and try again. & exit /b 1)

:: Start services with better error handling and logging
echo [1/4] Starting API Bridge...
start /min "API Bridge" cmd /c "echo [API Bridge] Starting... && python api_bridge.py --port 5000"
call :check_permission_error

:: Wait for API Bridge to be ready
echo [INFO] Waiting for API Bridge to initialize...
timeout /t 3 /nobreak >nul

echo [2/4] Starting MCP Backend...
start /min "MCP Backend" cmd /c "echo [MCP Backend] Starting... && python linkedin_browser_mcp.py --port 5001"
call :check_permission_error

echo [INFO] Waiting for MCP Backend to initialize...
timeout /t 2 /nobreak >nul

echo [3/4] Starting React Frontend...
start /min "React Frontend" cmd /c "echo [React Frontend] Starting... && npm start -- --port 5002"
call :check_permission_error

echo [INFO] Waiting for React Frontend to initialize...
timeout /t 2 /nobreak >nul

echo [4/4] Starting LLM Controller...
start /min "LLM Controller" cmd /c "echo [LLM Controller] Starting... && python llm_controller.py --port 5003"
call :check_permission_error

echo [INFO] Waiting for all services to be ready...

:end
if %PERMISSION_ERROR%==1 (
    echo.
    echo [FATAL] One or more services failed to start due to permission errors.
    echo [ACTION] Please close this window and re-run as administrator.
    pause
    exit /b 1
)

:: Wait for all services to be ready
timeout /t 3 /nobreak >nul

:: Open dashboard
echo [INFO] Opening dashboard in browser...
start "" http://localhost:3000

echo.
echo ========================================
echo [SUCCESS] All services started!
echo ========================================
echo.
echo Dashboard: http://localhost:3000
echo API Bridge: http://localhost:8001
echo.
echo [IMPORTANT] Configure your LinkedIn credentials in the Settings page!
echo.
echo Press any key to exit this window...
pause >nul 