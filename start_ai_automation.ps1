# AI Job Automation Background Runner
# This script runs the AI automation system in the background

Write-Host "Starting AI Job Automation in background..." -ForegroundColor Green

# Check if Python is available
try {
    python --version | Out-Null
} catch {
    Write-Host "Error: Python not found. Please install Python and try again." -ForegroundColor Red
    exit 1
}

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import aiohttp, asyncio, json, logging, time, os, shutil, datetime, typing, dataclasses, pathlib" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing required packages..." -ForegroundColor Yellow
        pip install aiohttp
    }
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    pip install aiohttp
}

# Check if Gemini is available (optional)
try {
    python -c "import google.generativeai" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Gemini AI available for enhanced matching" -ForegroundColor Green
    } else {
        Write-Host "Gemini not available. Install with: pip install google-generativeai" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Gemini not available. Install with: pip install google-generativeai" -ForegroundColor Yellow
}

# Create a Python script for continuous automation
$automationScript = @"
import asyncio
import sys
import os
from ai_job_automation import AIJobAutomation

async def run_automation():
    print("Starting AI Job Automation...")
    automation = AIJobAutomation()
    
    # You can customize preferences here
    automation.update_preferences(
        keywords=["python developer", "software engineer", "backend developer"],
        location="Remote",
        experience_level="mid-level",
        job_type="full-time",
        remote_preference=True,
        skills_required=["Python", "Django", "PostgreSQL"],
        skills_preferred=["React", "AWS", "Docker"]
    )
    
    print("Running continuous automation (every 30 minutes)...")
    print("Press Ctrl+C to stop")
    
    # Run continuous automation
    await automation.run_continuous_automation(interval_minutes=30)

if __name__ == "__main__":
    try:
        asyncio.run(run_automation())
    except KeyboardInterrupt:
        print("\nAutomation stopped by user")
    except Exception as e:
        print(f"Automation error: {e}")
"@

# Write the automation script to a temporary file
$scriptPath = "run_automation_temp.py"
$automationScript | Out-File -FilePath $scriptPath -Encoding UTF8

Write-Host "Starting automation in background..." -ForegroundColor Green
Write-Host "Logs will be saved to logs/automation.log" -ForegroundColor Cyan
Write-Host "To stop automation, close this window or press Ctrl+C" -ForegroundColor Yellow

# Run the automation script in background
Start-Process python -ArgumentList $scriptPath -WindowStyle Hidden

Write-Host "AI Automation started successfully!" -ForegroundColor Green
Write-Host "Check logs/automation.log for progress" -ForegroundColor Cyan
Write-Host "Access the dashboard at http://localhost:3000 for stats and control" -ForegroundColor Cyan

# Keep the script running to show status
while ($true) {
    if (Test-Path "logs/automation.log") {
        $lastLine = Get-Content "logs/automation.log" -Tail 1
        Write-Host "Latest log: $lastLine" -ForegroundColor Gray
    }
    Start-Sleep -Seconds 30
} 