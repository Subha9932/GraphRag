# Push to GitHub using GitHub Desktop's bundled Git
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GraphRAG - Push to GitHub via CLI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find GitHub Desktop's git
$gitPath = Get-ChildItem "C:\Users\202317\AppData\Local\GitHubDesktop" -Recurse -Filter "git.exe" -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -like "*\cmd\git.exe" } | 
    Select-Object -First 1 -ExpandProperty FullName

if (-not $gitPath) {
    Write-Host "ERROR: Could not find git.exe from GitHub Desktop" -ForegroundColor Red
    Write-Host "Please use GitHub Desktop GUI instead" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Found Git at: $gitPath" -ForegroundColor Green
Write-Host ""

# Navigate to project directory
Set-Location "c:\Users\202317\.gemini\antigravity\scratch\GrapgRagMain"

Write-Host "Step 1: Initializing repository..." -ForegroundColor Yellow
& $gitPath init

Write-Host "Step 2: Adding all files..." -ForegroundColor Yellow
& $gitPath add .

Write-Host "Step 3: Committing changes..." -ForegroundColor Yellow
& $gitPath commit -m "Initial commit: GraphRAG Codebase Analysis Tool"

Write-Host "Step 4: Setting main branch..." -ForegroundColor Yellow
& $gitPath branch -M main

Write-Host "Step 5: Adding remote..." -ForegroundColor Yellow
& $gitPath remote add origin https://github.com/Subha9932/GraphRag.git

Write-Host "Step 6: Pushing to GitHub..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "When prompted:" -ForegroundColor Cyan
Write-Host "Username: Subha9932" -ForegroundColor White
Write-Host "Password: Your GitHub password or token" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& $gitPath push -u origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Push complete!" -ForegroundColor Green
Write-Host "Visit: https://github.com/Subha9932/GraphRag" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

pause
