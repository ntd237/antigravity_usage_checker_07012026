# Antigravity Usage Checker - Install Script for Windows
# Author: ntd237

Write-Host ""
Write-Host "🚀 Antigravity Usage Checker - Installation" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow

$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -ge 3 -and $minor -ge 8) {
                $pythonCmd = $cmd
                Write-Host "✅ Found $version" -ForegroundColor Green
                break
            }
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "❌ Python 3.8+ not found!" -ForegroundColor Red
    Write-Host "   Please install Python from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check pip
Write-Host ""
Write-Host "🔍 Checking pip..." -ForegroundColor Yellow
try {
    & $pythonCmd -m pip --version | Out-Null
    Write-Host "✅ pip is available" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found!" -ForegroundColor Red
    exit 1
}

# Clone/Download repository
Write-Host ""
Write-Host "📦 Setting up Antigravity Usage Checker..." -ForegroundColor Yellow

$repoUrl = "https://github.com/ntd237/antigravity_usage_checker_07012026.git"
$installDir = "$env:USERPROFILE\.agusage"

# Check if git is available
$hasGit = $false
try {
    git --version | Out-Null
    $hasGit = $true
} catch {
    Write-Host "⚠️  Git not found, will download as ZIP" -ForegroundColor Yellow
}

if ($hasGit) {
    Write-Host "📥 Cloning repository..." -ForegroundColor Yellow
    
    if (Test-Path $installDir) {
        Write-Host "   Directory exists, pulling latest..." -ForegroundColor Yellow
        Push-Location $installDir
        git pull
        Pop-Location
    } else {
        git clone $repoUrl $installDir
    }
} else {
    Write-Host "📥 Downloading repository..." -ForegroundColor Yellow
    $zipUrl = "https://github.com/ntd237/antigravity_usage_checker_07012026/archive/refs/heads/main.zip"
    $zipFile = "$env:TEMP\agusage.zip"
    
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile
    Expand-Archive -Path $zipFile -DestinationPath $env:TEMP -Force
    
    if (Test-Path $installDir) {
        Remove-Item -Path $installDir -Recurse -Force
    }
    
    Move-Item -Path "$env:TEMP\antigravity_usage_checker_07012026-main" -Destination $installDir
    Remove-Item -Path $zipFile
}

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
Push-Location $installDir

& $pythonCmd -m pip install --upgrade pip
& $pythonCmd -m pip install -r requirements.txt

# Install package
Write-Host ""
Write-Host "🔧 Installing agusage command..." -ForegroundColor Yellow
& $pythonCmd -m pip install -e .

Pop-Location

# Verify installation
Write-Host ""
Write-Host "✅ Verifying installation..." -ForegroundColor Yellow

try {
    $version = agusage --version 2>&1
    Write-Host "✅ Installation successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "─────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host "🎉 Antigravity Usage Checker installed!" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  agusage              Check quota" -ForegroundColor White
    Write-Host "  agusage --verbose    Debug mode" -ForegroundColor White
    Write-Host "  agusage --no-cache   Disable cache" -ForegroundColor White
    Write-Host ""
    Write-Host "GitHub: https://github.com/ntd237/antigravity_usage_checker_07012026" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "⚠️  Command 'agusage' not found in PATH" -ForegroundColor Yellow
    Write-Host "   You may need to restart your terminal or add Python Scripts to PATH" -ForegroundColor Yellow
    Write-Host ""
}
