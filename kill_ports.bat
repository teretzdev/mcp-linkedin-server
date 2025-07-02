@echo off
echo Killing processes on commonly used ports...
echo.

echo Checking for processes on port 3000 (React Frontend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo Killing process %%a on port 3000
    taskkill /PID %%a /F >nul 2>&1
)

echo Checking for processes on port 8001 (API Bridge)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    echo Killing process %%a on port 8001
    taskkill /PID %%a /F >nul 2>&1
)

echo Checking for processes on port 8002 (API Bridge backup)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo Killing process %%a on port 8002
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Port cleanup complete!
echo.
pause 