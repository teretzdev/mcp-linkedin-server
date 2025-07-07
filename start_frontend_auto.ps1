# LinkedIn MCP Frontend Auto-Start Script
# Automatically finds available ports and handles conflicts

Write-Host "Starting LinkedIn MCP Frontend..." -ForegroundColor Green
Write-Host ""

# Function to check if port is available
function Test-PortAvailable {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $false
    }
    catch {
        return $true
    }
}

# Function to kill process on specific port
function Stop-ProcessOnPort {
    param([int]$Port)
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        foreach ($process in $processes) {
            $proc = Get-Process -Id $process.OwningProcess -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Killing process on port $Port: $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Yellow
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
        }
    }
    catch {
        Write-Host "No process found on port $Port" -ForegroundColor Gray
    }
}

# Function to find available port
function Find-AvailablePort {
    param([int]$StartPort = 3000, [int]$MaxAttempts = 10)
    
    for ($i = 0; $i -lt $MaxAttempts; $i++) {
        $port = $StartPort + $i
        if (Test-PortAvailable -Port $port) {
            return $port
        }
    }
    return $null
}

# Kill existing processes on common React ports
Write-Host "Checking for existing React processes..." -ForegroundColor Cyan
@(3000, 3001, 3002, 3003, 3004, 3005) | ForEach-Object {
    Stop-ProcessOnPort -Port $_
}

# Find available port
Write-Host "Finding available port..." -ForegroundColor Cyan
$availablePort = Find-AvailablePort -StartPort 3000

if ($availablePort) {
    Write-Host "Starting React app on port $availablePort..." -ForegroundColor Green
    
    # Set environment variable for React
    $env:PORT = $availablePort
    
    # Start React app
    try {
        npm start
    }
    catch {
        Write-Host "Failed to start React app: $_" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "No available ports found in range 3000-3009" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "React app should now be running on http://localhost:$availablePort" -ForegroundColor Green
Write-Host "" 