@echo off
setlocal enabledelayedexpansion

echo Starting LinkedIn MCP Frontend (Auto Mode)...
echo.

:: Function to find available port starting from 3000
set "port=3000"
:check_port
netstat -ano | findstr ":%port%" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo Port %port% is in use, trying next port...
    set /a port+=1
    goto check_port
)

echo Starting React development server on http://localhost:%port%
echo Make sure the API bridge is running on http://localhost:8001
echo.

:: Set PORT environment variable to use the available port
set PORT=%port%

:: Start npm with the specific port
npm start -- --port %port%

endlocal 