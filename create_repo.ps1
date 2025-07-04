# PowerShell script to create GitHub repository and push code
# This script will help you create a new repository under your teretzdev account

Write-Host "=== GitHub Repository Creation Script ===" -ForegroundColor Green
Write-Host ""

# Check if we have a GitHub token
$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Host "No GitHub token found. You'll need to create one:" -ForegroundColor Yellow
    Write-Host "1. Go to https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "2. Click 'Generate new token (classic)'" -ForegroundColor Cyan
    Write-Host "3. Give it a name like 'Repo Creation'" -ForegroundColor Cyan
    Write-Host "4. Select 'repo' scope" -ForegroundColor Cyan
    Write-Host "5. Copy the token" -ForegroundColor Cyan
    Write-Host ""
    $token = Read-Host "Enter your GitHub Personal Access Token"
}

if (-not $token) {
    Write-Host "No token provided. Exiting." -ForegroundColor Red
    exit 1
}

# Set the token as environment variable
$env:GITHUB_TOKEN = $token

Write-Host "Creating repository 'mcp-linkedin-server' under teretzdev account..." -ForegroundColor Green

# Create the repository using GitHub API
$repoData = @{
    name = "mcp-linkedin-server"
    description = "LinkedIn Job Hunter with AI Automation and MCP Integration"
    private = $false
    auto_init = $false
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" `
        -Method POST `
        -Headers @{
            "Authorization" = "token $token"
            "Accept" = "application/vnd.github.v3+json"
            "User-Agent" = "PowerShell"
        } `
        -Body $repoData `
        -ContentType "application/json"
    
    Write-Host "Repository created successfully!" -ForegroundColor Green
    Write-Host "Repository URL: $($response.html_url)" -ForegroundColor Cyan
    
    # Add the new remote
    Write-Host "Adding remote origin..." -ForegroundColor Green
    git remote add origin "https://github.com/teretzdev/mcp-linkedin-server.git"
    
    # Push the code
    Write-Host "Pushing code to repository..." -ForegroundColor Green
    git push -u origin master
    
    Write-Host ""
    Write-Host "=== SUCCESS! ===" -ForegroundColor Green
    Write-Host "Your repository is now available at: $($response.html_url)" -ForegroundColor Cyan
    Write-Host "You can now continue with development and push changes normally." -ForegroundColor Green
    
} catch {
    Write-Host "Error creating repository: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.Exception.Response)" -ForegroundColor Red
    exit 1
} 