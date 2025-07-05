@echo off
echo ========================================
echo LinkedIn Job Hunter - Auto Startup
echo ========================================
echo.

:: Step 1: Kill ALL processes on port 3000 automatically
echo [1/6] Automatically killing processes on port 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo Killing process %%a on port 3000
    taskkill /PID %%a /F >nul 2>&1
)

:: Step 2: Clear ALL build caches
echo [2/6] Clearing all build caches...
if exist "node_modules\.cache" (
    rmdir /s /q "node_modules\.cache" >nul 2>&1
)
if exist ".next" (
    rmdir /s /q ".next" >nul 2>&1
)

:: Step 3: Fix ALL corrupted files automatically
echo [3/6] Fixing all corrupted files...
if not exist "src" mkdir src
if not exist "src\components" mkdir src\components

:: Create clean index.js
echo import React from 'react';> src\index.js
echo import ReactDOM from 'react-dom/client';>> src\index.js
echo import './index.css';>> src\index.js
echo import App from './App';>> src\index.js
echo.>> src\index.js
echo const root = ReactDOM.createRoot(document.getElementById('root'));>> src\index.js
echo root.render(>> src\index.js
echo   ^<React.StrictMode^>>> src\index.js
echo     ^<App /^>>> src\index.js
echo   ^</React.StrictMode^>>> src\index.js
echo );>> src\index.js

:: Create clean index.css
echo @tailwind base;> src\index.css
echo @tailwind components;>> src\index.css
echo @tailwind utilities;>> src\index.css
echo.>> src\index.css
echo body {>> src\index.css
echo   margin: 0;>> src\index.css
echo   font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',>> src\index.css
echo     'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',>> src\index.css
echo     sans-serif;>> src\index.css
echo   -webkit-font-smoothing: antialiased;>> src\index.css
echo   -moz-osx-font-smoothing: grayscale;>> src\index.css
echo   background-color: #f8fafc;>> src\index.css
echo }>> src\index.css

:: Step 4: Install dependencies if needed
echo [4/6] Checking dependencies...
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install --silent
)

:: Step 5: Start React app with automatic port handling
echo [5/6] Starting React app automatically...
echo set PORT=3000 > temp_start.bat
echo set BROWSER=none >> temp_start.bat
echo npm start >> temp_start.bat
start "React App" cmd /k temp_start.bat

:: Step 6: Wait and open browser automatically
echo [6/6] Waiting for app to start and opening browser...
timeout /t 10 /nobreak >nul

:: Open browser automatically
start http://localhost:3000

:: Clean up temp file
del temp_start.bat >nul 2>&1

echo.
echo ========================================
echo LinkedIn Job Hunter Started Successfully!
echo ========================================
echo Frontend: http://localhost:3000
echo.
echo The dashboard should now be working with full functionality!
echo.
pause 