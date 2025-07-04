# Simple script to set up repository connection
Write-Host "=== Repository Setup ===" -ForegroundColor Green
Write-Host ""

Write-Host "Please follow these steps:" -ForegroundColor Yellow
Write-Host "1. Go to https://github.com/new" -ForegroundColor Cyan
Write-Host "2. Repository name: mcp-linkedin-server" -ForegroundColor Cyan
Write-Host "3. Description: LinkedIn Job Hunter with AI automation" -ForegroundColor Cyan
Write-Host "4. Make it Public or Private (your choice)" -ForegroundColor Cyan
Write-Host "5. DO NOT initialize with README, .gitignore, or license" -ForegroundColor Cyan
Write-Host "6. Click 'Create repository'" -ForegroundColor Cyan
Write-Host ""

$continue = Read-Host "Have you created the repository? (y/n)"
if ($continue -eq "y" -or $continue -eq "Y") {
    Write-Host ""
    Write-Host "Setting up remote connection..." -ForegroundColor Green
    
    # Add the new remote
    git remote add origin https://github.com/teretzdev/mcp-linkedin-server.git
    
    # Push the code
    Write-Host "Pushing code to repository..." -ForegroundColor Green
    git push -u origin master
    
    Write-Host ""
    Write-Host "=== SUCCESS ===" -ForegroundColor Green
    Write-Host "Your repository is now available at:" -ForegroundColor Cyan
    Write-Host "https://github.com/teretzdev/mcp-linkedin-server" -ForegroundColor Cyan
} else {
    Write-Host "Please create the repository first and then run this script again." -ForegroundColor Yellow
} 