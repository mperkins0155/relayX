# Pre-Deployment Verification Script
# Run this before deploying to catch common issues

Write-Host "RelayX Pre-Deployment Verification" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

$errors = 0
$warnings = 0

# Check if Git is initialized
Write-Host "Checking Git status..." -ForegroundColor Yellow
if (Test-Path .git) {
    Write-Host "[OK] Git repository initialized" -ForegroundColor Green
    
    # Check if remote is set
    $remote = git remote -v 2>&1
    if ($remote -match "origin") {
        Write-Host "[OK] Git remote configured" -ForegroundColor Green
    } else {
        Write-Host "[WARN] No Git remote found. Add with: git remote add origin URL" -ForegroundColor Red
        $warnings++
    }
} else {
    Write-Host "[ERROR] No Git repository found" -ForegroundColor Red
    $errors++
}

# Check for required files
Write-Host "`nChecking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "vercel.json",
    "railway.toml",
    "backend\requirements.txt",
    "backend\main.py",
    "frontend\package.json",
    "db\schema.sql",
    "SIMPLE_DEPLOYMENT.md",
    "DEPLOYMENT_CHECKLIST.md"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "[OK] $file" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] $file missing" -ForegroundColor Red
        $errors++
    }
}

# Check for environment variable templates
Write-Host "`nChecking environment templates..." -ForegroundColor Yellow
if (Test-Path "VERCEL_ENV.txt") {
    Write-Host "[OK] VERCEL_ENV.txt found" -ForegroundColor Green
} else {
    Write-Host "[WARN] VERCEL_ENV.txt not found" -ForegroundColor Yellow
    $warnings++
}

if (Test-Path "RAILWAY_ENV.txt") {
    Write-Host "[OK] RAILWAY_ENV.txt found" -ForegroundColor Green
} else {
    Write-Host "[WARN] RAILWAY_ENV.txt not found" -ForegroundColor Yellow
    $warnings++
}

# Check if frontend dependencies are installed
Write-Host "`nChecking frontend setup..." -ForegroundColor Yellow
if (Test-Path "frontend\node_modules") {
    Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[WARN] Frontend dependencies not installed. Run: cd frontend; npm install" -ForegroundColor Yellow
    $warnings++
}

# Check if backend is Python 3.11
Write-Host "`nChecking Python version..." -ForegroundColor Yellow
if (Test-Path "backend\runtime.txt") {
    $pythonVersion = Get-Content "backend\runtime.txt"
    Write-Host "[OK] Runtime specified: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[WARN] No runtime.txt found" -ForegroundColor Yellow
    $warnings++
}

# Summary
Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

if (($errors -eq 0) -and ($warnings -eq 0)) {
    Write-Host "[SUCCESS] All checks passed! Ready to deploy." -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Push to GitHub: git push origin main" -ForegroundColor White
    Write-Host "2. Follow SIMPLE_DEPLOYMENT.md" -ForegroundColor White
    Write-Host "3. Use DEPLOYMENT_CHECKLIST.md to track progress" -ForegroundColor White
} else {
    if ($errors -gt 0) {
        Write-Host "[ERROR] $errors error(s) found - please fix before deploying" -ForegroundColor Red
    }
    if ($warnings -gt 0) {
        Write-Host "[WARN] $warnings warning(s) found - recommended to address" -ForegroundColor Yellow
    }
}

Write-Host "`nDeployment Resources:" -ForegroundColor Cyan
Write-Host "- Vercel: https://vercel.com/new" -ForegroundColor White
Write-Host "- Railway: https://railway.app/new" -ForegroundColor White
Write-Host "- Supabase: https://supabase.com/dashboard" -ForegroundColor White

Write-Host "`n"
