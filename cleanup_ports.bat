@echo off
echo ========================================
echo LinkedIn Job Hunter - Port Cleanup
echo ========================================
echo.

echo [INFO] Cleaning up ports 3000, 8001, 8002...

:: Kill processes on port 3000
netstat -ano | findstr ":3000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Killing processes on port 3000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
        taskkill /PID %%a /F >nul 2>&1
        echo [SUCCESS] Killed process %%a on port 3000
    )
) else (
    echo [INFO] Port 3000 is clean
)

:: Kill processes on port 8001
netstat -ano | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Killing processes on port 8001...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
        taskkill /PID %%a /F >nul 2>&1
        echo [SUCCESS] Killed process %%a on port 8001
    )
) else (
    echo [INFO] Port 8001 is clean
)

:: Kill processes on port 8002
netstat -ano | findstr ":8002" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Killing processes on port 8002...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002" ^| findstr "LISTENING"') do (
        taskkill /PID %%a /F >nul 2>&1
        echo [SUCCESS] Killed process %%a on port 8002
    )
) else (
    echo [INFO] Port 8002 is clean
)

echo.
echo [SUCCESS] Port cleanup complete!
echo.
echo You can now run: ./start_all.bat
echo.
pause 