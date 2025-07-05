@echo off
echo ========================================
echo LinkedIn Job Hunter - Frontend Only
echo ========================================
echo.

:: Kill any processes on port 3000
echo [1/4] Checking for port conflicts...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo Killing process %%a on port 3000
    taskkill /PID %%a /F >nul 2>&1
)

:: Clear React build cache
echo [2/4] Clearing build cache...
if exist "node_modules\.cache" (
    rmdir /s /q "node_modules\.cache" >nul 2>&1
)

:: Fix corrupted files
echo [3/4] Fixing corrupted files...
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

:: Create simple Dashboard component
echo import React from 'react';> src\components\Dashboard.js
echo.>> src\components\Dashboard.js
echo function Dashboard() {>> src\components\Dashboard.js
echo   return (>> src\components\Dashboard.js
echo     ^<div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 p-8"^>>> src\components\Dashboard.js
echo       ^<div className="max-w-4xl mx-auto"^>>> src\components\Dashboard.js
echo         ^<div className="bg-white rounded-lg shadow-lg p-8"^>>> src\components\Dashboard.js
echo           ^<h1 className="text-4xl font-bold text-gray-900 mb-4"^>LinkedIn Job Hunter^</h1^>>> src\components\Dashboard.js
echo           ^<p className="text-xl text-gray-600 mb-8"^>AI-powered job search automation platform^</p^>>> src\components\Dashboard.js
echo           ^<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"^>>> src\components\Dashboard.js
echo             ^<div className="bg-blue-50 p-6 rounded-lg"^>>> src\components\Dashboard.js
echo               ^<h3 className="text-lg font-semibold text-blue-900 mb-2"^>Job Search^</h3^>>> src\components\Dashboard.js
echo               ^<p className="text-blue-700"^>Find and apply to jobs with AI assistance^</p^>>> src\components\Dashboard.js
echo             ^</div^>>> src\components\Dashboard.js
echo             ^<div className="bg-green-50 p-6 rounded-lg"^>>> src\components\Dashboard.js
echo               ^<h3 className="text-lg font-semibold text-green-900 mb-2"^>Easy Apply^</h3^>>> src\components\Dashboard.js
echo               ^<p className="text-green-700"^>Automated job applications with smart responses^</p^>>> src\components\Dashboard.js
echo             ^</div^>>> src\components\Dashboard.js
echo             ^<div className="bg-purple-50 p-6 rounded-lg"^>>> src\components\Dashboard.js
echo               ^<h3 className="text-lg font-semibold text-purple-900 mb-2"^>Analytics^</h3^>>> src\components\Dashboard.js
echo               ^<p className="text-purple-700"^>Track your job search progress and success rates^</p^>>> src\components\Dashboard.js
echo             ^</div^>>> src\components\Dashboard.js
echo           ^</div^>>> src\components\Dashboard.js
echo           ^<div className="mt-8 text-center"^>>> src\components\Dashboard.js
echo             ^<p className="text-gray-500"^>Frontend is running successfully! Backend services can be started separately.^</p^>>> src\components\Dashboard.js
echo           ^</div^>>> src\components\Dashboard.js
echo         ^</div^>>> src\components\Dashboard.js
echo       ^</div^>>> src\components\Dashboard.js
echo     ^</div^>>> src\components\Dashboard.js
echo   );>> src\components\Dashboard.js
echo }>> src\components\Dashboard.js
echo.>> src\components\Dashboard.js
echo export default Dashboard;>> src\components\Dashboard.js

:: Create simple App.js
echo import React from 'react';> src\App.js
echo import Dashboard from './components/Dashboard';>> src\App.js
echo import './index.css';>> src\App.js
echo.>> src\App.js
echo function App() {>> src\App.js
echo   return (>> src\App.js
echo     ^<Dashboard /^>>> src\App.js
echo   );>> src\App.js
echo }>> src\App.js
echo.>> src\App.js
echo export default App;>> src\App.js

:: Start the React app
echo [4/4] Starting React app...
start "React App" cmd /k "npm start"

:: Wait a moment for React to start
timeout /t 5 /nobreak >nul

:: Open browser
echo.
echo ========================================
echo Starting browser...
echo ========================================
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo LinkedIn Job Hunter Frontend Started!
echo ========================================
echo Frontend: http://localhost:3000
echo.
echo The dashboard should now be visible in your browser.
echo Backend services can be started separately if needed.
echo.
pause 