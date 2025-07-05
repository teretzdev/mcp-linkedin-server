@echo off
REM Kill any process using port 8001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001 ^| findstr LISTENING') do (
    echo Killing process on port 8001 with PID %%a
    taskkill /PID %%a /F
)
REM Start the backend server
python api_bridge_with_database.py 