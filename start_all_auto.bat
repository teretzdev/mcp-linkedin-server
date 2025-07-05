@echo off
setlocal enabledelayedexpansion

echo ========================================
echo LinkedIn Job Hunter - Fully Automated Startup
echo ========================================
echo.

:: Check for .env file and create if missing
if not exist ".env" (
    echo [INFO] Creating .env file...
    python create_env.py
    if errorlevel 1 (
        echo [ERROR] Failed to create .env file
        exit /b 1
    )
    echo.
)

:: Automated process cleanup - kill conflicting processes
echo [INFO] Checking for conflicting processes...

:: Function to check and kill process on port
set "ports_to_check=3000 8001 8002 8000"
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
echo [INFO] Starting services with automated configuration...
echo.

:: Start API Bridge with auto-retry
echo [1/4] Starting API Bridge...
start /min "API Bridge" cmd /c "echo [API Bridge] Starting... && python api_bridge.py"
timeout /t 3 /nobreak >nul

:: Verify API Bridge is running
:check_api_bridge
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo [INFO] Waiting for API Bridge to be ready...
    timeout /t 2 /nobreak >nul
    goto check_api_bridge
)
echo [SUCCESS] API Bridge is running

:: Start MCP Backend
echo [2/4] Starting MCP Backend...
start /min "MCP Backend" cmd /c "echo [MCP Backend] Starting... && python linkedin_browser_mcp.py"
timeout /t 2 /nobreak >nul

:: Find available port for React
set "react_port=3000"
:check_react_port
netstat -ano | findstr ":%react_port%" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    set /a react_port+=1
    goto check_react_port
)

:: Start React Frontend with specific port
echo [3/4] Starting React Frontend on port %react_port%...
set PORT=%react_port%
start /min "React Frontend" cmd /c "echo [React Frontend] Starting on port %react_port%... && npm start -- --port %react_port%"
timeout /t 5 /nobreak >nul

:: Verify React is running
:check_react
curl -s http://localhost:%react_port% >nul 2>&1
if errorlevel 1 (
    echo [INFO] Waiting for React Frontend to be ready...
    timeout /t 2 /nobreak >nul
    goto check_react
)
echo [SUCCESS] React Frontend is running on port %react_port%

:: Start LLM Controller
echo [4/4] Starting LLM Controller...
start /min "LLM Controller" cmd /c "echo [LLM Controller] Starting... && python llm_controller.py"
timeout /t 3 /nobreak >nul

:: Open dashboard with correct port
echo [INFO] Opening dashboard in browser...
start "" http://localhost:%react_port%

echo.
echo ========================================
echo [SUCCESS] All services started automatically!
echo ========================================
echo.
echo Dashboard: http://localhost:%react_port%
echo API Bridge: http://localhost:8001
echo.
echo [IMPORTANT] Configure your LinkedIn credentials in the Settings page!
echo.
echo Press any key to exit this window...
pause >nul

REM Kill any process using port 8001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001 ^| findstr LISTENING') do (
    echo Killing process on port 8001 with PID %%a
    taskkill /PID %%a /F
)
REM Start the backend server in a new window
start "Backend" cmd /c "python api_bridge_with_database.py"
REM Wait for backend to be ready
ping 127.0.0.1 -n 10 > nul
REM Run the test suite
pytest --maxfail=10 --disable-warnings -v

endlocal 