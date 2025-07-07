@echo off
REM IMPORTANT: Run this script in CMD, not PowerShell!
echo Starting LinkedIn MCP Frontend...
echo.
echo This will start the React development server on the next available port
echo Make sure the API bridge is running on http://localhost:8000
echo.

REM Kill any existing React processes on ports 3000-3010
echo Checking for existing React processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    echo Killing process on port 3000: %%a
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3001') do (
    echo Killing process on port 3001: %%a
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3002') do (
    echo Killing process on port 3002: %%a
    taskkill /F /PID %%a 2>nul
)

REM Start React with automatic port finding
echo Starting React app with automatic port detection...
set PORT=3000
npm start -- --port %PORT%

REM If the above fails, try the next port
if errorlevel 1 (
    echo Port 3000 busy, trying 3001...
    set PORT=3001
    npm start -- --port %PORT%
)

REM If that fails too, try 3002
if errorlevel 1 (
    echo Port 3001 busy, trying 3002...
    set PORT=3002
    npm start -- --port %PORT%
)

echo.
echo React app should now be running on http://localhost:%PORT%
echo. 