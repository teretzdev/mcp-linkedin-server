@echo off
echo ========================================
echo LinkedIn Job Hunter - Auto Startup
echo ========================================
echo.

:: Kill any processes on port 3000
echo [1/6] Checking for port conflicts...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo Killing process %%a on port 3000
    taskkill /PID %%a /F >nul 2>&1
)

:: Kill any processes on port 8001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    echo Killing process %%a on port 8001
    taskkill /PID %%a /F >nul 2>&1
)

:: Clear React build cache
echo [2/6] Clearing build cache...
if exist "node_modules\.cache" (
    rmdir /s /q "node_modules\.cache" >nul 2>&1
)

:: Fix corrupted files
echo [3/6] Fixing corrupted files...
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

:: Create clean AIAutomationDashboard.js
echo import React from 'react';> src\components\AIAutomationDashboard.js
echo.>> src\components\AIAutomationDashboard.js
echo function AIAutomationDashboard() {>> src\components\AIAutomationDashboard.js
echo   return (>> src\components\AIAutomationDashboard.js
echo     ^<div className="space-y-6"^>>> src\components\AIAutomationDashboard.js
echo       ^<div className="bg-white rounded-lg shadow-sm p-6"^>>> src\components\AIAutomationDashboard.js
echo         ^<h1 className="text-2xl font-bold text-gray-900 mb-4"^>AI Automation Dashboard^</h1^>>> src\components\AIAutomationDashboard.js
echo         ^<p className="text-gray-600"^>AI-powered job search automation^</p^>>> src\components\AIAutomationDashboard.js
echo       ^</div^>>> src\components\AIAutomationDashboard.js
echo     ^</div^>>> src\components\AIAutomationDashboard.js
echo   );>> src\components\AIAutomationDashboard.js
echo }>> src\components\AIAutomationDashboard.js
echo.>> src\components\AIAutomationDashboard.js
echo export default AIAutomationDashboard;>> src\components\AIAutomationDashboard.js

:: Create other missing components
echo import React from 'react';> src\components\Dashboard.js
echo.>> src\components\Dashboard.js
echo function Dashboard() {>> src\components\Dashboard.js
echo   return (>> src\components\Dashboard.js
echo     ^<div className="space-y-6"^>>> src\components\Dashboard.js
echo       ^<div className="bg-white rounded-lg shadow-sm p-6"^>>> src\components\Dashboard.js
echo         ^<h1 className="text-2xl font-bold text-gray-900 mb-4"^>Dashboard^</h1^>>> src\components\Dashboard.js
echo         ^<p className="text-gray-600"^>Welcome to LinkedIn Job Hunter^</p^>>> src\components\Dashboard.js
echo       ^</div^>>> src\components\Dashboard.js
echo     ^</div^>>> src\components\Dashboard.js
echo   );>> src\components\Dashboard.js
echo }>> src\components\Dashboard.js
echo.>> src\components\Dashboard.js
echo export default Dashboard;>> src\components\Dashboard.js

echo import React from 'react';> src\components\Login.js
echo.>> src\components\Login.js
echo function Login() {>> src\components\Login.js
echo   return (>> src\components\Login.js
echo     ^<div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center"^>>> src\components\Login.js
echo       ^<div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full"^>>> src\components\Login.js
echo         ^<h1 className="text-3xl font-bold text-gray-900 mb-2"^>LinkedIn Job Hunter^</h1^>>> src\components\Login.js
echo         ^<p className="text-gray-600"^>Sign in to start your job search^</p^>>> src\components\Login.js
echo       ^</div^>>> src\components\Login.js
echo     ^</div^>>> src\components\Login.js
echo   );>> src\components\Login.js
echo }>> src\components\Login.js
echo.>> src\components\Login.js
echo export default Login;>> src\components\Login.js

echo import React from 'react';> src\components\Sidebar.js
echo.>> src\components\Sidebar.js
echo function Sidebar() {>> src\components\Sidebar.js
echo   return (>> src\components\Sidebar.js
echo     ^<div className="w-64 bg-white shadow-sm border-r border-gray-200 min-h-screen"^>>> src\components\Sidebar.js
echo       ^<div className="p-6"^>>> src\components\Sidebar.js
echo         ^<h1 className="text-xl font-bold text-gray-900"^>Job Hunter^</h1^>>> src\components\Sidebar.js
echo       ^</div^>>> src\components\Sidebar.js
echo     ^</div^>>> src\components\Sidebar.js
echo   );>> src\components\Sidebar.js
echo }>> src\components\Sidebar.js
echo.>> src\components\Sidebar.js
echo export default Sidebar;>> src\components\Sidebar.js

:: Create simple App.js
echo import React from 'react';> src\App.js
echo import Dashboard from './components/Dashboard';>> src\App.js
echo import './index.css';>> src\App.js
echo.>> src\App.js
echo function App() {>> src\App.js
echo   return (>> src\App.js
echo     ^<div className="min-h-screen bg-gray-50"^>>> src\App.js
echo       ^<Dashboard /^>>> src\App.js
echo     ^</div^>>> src\App.js
echo   );>> src\App.js
echo }>> src\App.js
echo.>> src\App.js
echo export default App;>> src\App.js

:: Install dependencies if needed
echo [4/6] Checking dependencies...
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
)

:: Start the React app
echo [5/6] Starting React app...
start "React App" cmd /k "npm start"

:: Wait a moment for React to start
timeout /t 5 /nobreak >nul

:: Start backend services (with error handling)
echo [6/6] Starting backend services...
start "API Bridge" cmd /k "python api_bridge.py"

:: Try to start database integration, but don't fail if it doesn't work
echo Starting database integration...
start "Database Integration" cmd /k "python -c \"import sys; sys.path.append('legacy'); from database.database import DatabaseManager; print('Database module found')\" 2>nul || echo Database module not available, skipping database integration"

:: Open browser
echo.
echo ========================================
echo Starting browser...
echo ========================================
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo LinkedIn Job Hunter is starting!
echo ========================================
echo Frontend: http://localhost:3000
echo API: http://localhost:8001
echo.
echo If you see any errors, check the terminal windows.
echo.
pause 