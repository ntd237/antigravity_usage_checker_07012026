# Antigravity Usage Checker - Install Script for Windows
# Repository: https://github.com/ntd237/antigravity_usage_checker_07012026

# Set encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Antigravity Usage Checker - Installer  " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[*] Checking Python installation..." -ForegroundColor Yellow

$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -ge 3 -and $minor -ge 8) {
                $pythonCmd = $cmd
                Write-Host "[OK] Found $version" -ForegroundColor Green
                break
            }
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python 3.8+ not found!" -ForegroundColor Red
    Write-Host "        Please install Python from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check pip
Write-Host ""
Write-Host "[*] Checking pip..." -ForegroundColor Yellow
try {
    & $pythonCmd -m pip --version | Out-Null
    Write-Host "[OK] pip is available" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] pip not found!" -ForegroundColor Red
    exit 1
}

# Clone/Download repository
Write-Host ""
Write-Host "[*] Setting up Antigravity Usage Checker..." -ForegroundColor Yellow

$repoUrl = "https://github.com/ntd237/antigravity_usage_checker_07012026.git"
$installDir = "$env:USERPROFILE\.agusage"

# Check if git is available
$hasGit = $false
try {
    git --version 2>&1 | Out-Null
    $hasGit = $true
} catch {
    Write-Host "[!] Git not found, will download as ZIP" -ForegroundColor Yellow
}

if ($hasGit) {
    Write-Host "[*] Cloning repository..." -ForegroundColor Yellow
    
    if (Test-Path $installDir) {
        Write-Host "    Directory exists, pulling latest..." -ForegroundColor Yellow
        Push-Location $installDir
        try {
            git pull 2>&1 | Out-Null
        } catch {
            Write-Host "[!] Git pull failed, continuing..." -ForegroundColor Yellow
        }
        Pop-Location
    } else {
        try {
            git clone $repoUrl $installDir 2>&1 | Out-Null
        } catch {
            Write-Host "[ERROR] Git clone failed!" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "[*] Downloading repository..." -ForegroundColor Yellow
    $zipUrl = "https://github.com/ntd237/antigravity_usage_checker_07012026/archive/refs/heads/main.zip"
    $zipFile = "$env:TEMP\agusage.zip"
    
    try {
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing
        
        if (Test-Path $installDir) {
            Remove-Item -Path $installDir -Recurse -Force
        }
        
        Expand-Archive -Path $zipFile -DestinationPath $env:TEMP -Force
        Move-Item -Path "$env:TEMP\antigravity_usage_checker_07012026-main" -Destination $installDir -Force
        Remove-Item -Path $zipFile -Force
    } catch {
        Write-Host "[ERROR] Download failed: $_" -ForegroundColor Red
        exit 1
    }
}

# Verify install directory exists
if (-not (Test-Path $installDir)) {
    Write-Host "[ERROR] Installation directory not found!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "$installDir\setup.py")) {
    Write-Host "[ERROR] setup.py not found in $installDir" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
Push-Location $installDir

try {
    & $pythonCmd -m pip install --upgrade pip --quiet 2>&1 | Out-Null
    & $pythonCmd -m pip install -r requirements.txt --quiet
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to install dependencies: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Install package
Write-Host ""
Write-Host "[*] Installing agcheck command..." -ForegroundColor Yellow
try {
    & $pythonCmd -m pip install -e . --quiet
    Write-Host "[OK] Package installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to install package: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

# Verify installation
Write-Host ""
Write-Host "[*] Verifying installation..." -ForegroundColor Yellow

# Try to find agcheck in PATH
$agcheckFound = $false
try {
    $result = & $pythonCmd -c "import src.cli; print('ok')" 2>&1
    if ($result -eq "ok") {
        $agcheckFound = $true
    }
} catch {}

# Also check if command exists
try {
    Get-Command agcheck -ErrorAction Stop | Out-Null
    $agcheckFound = $true
} catch {}

if ($agcheckFound) {
    Write-Host "[OK] Installation successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "  Antigravity Usage Checker installed!   " -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  agcheck              Check quota" -ForegroundColor White
    Write-Host "  agcheck --verbose    Debug mode" -ForegroundColor White
    Write-Host "  agcheck --no-cache   Disable cache" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "[!] Command 'agcheck' not found in PATH" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please restart your terminal and try:" -ForegroundColor Yellow
    Write-Host "  agcheck" -ForegroundColor White
    Write-Host ""
    Write-Host "If still not working, add Python Scripts to PATH:" -ForegroundColor Yellow
    
    # Get Python Scripts directory
    $scriptsDir = & $pythonCmd -c "import sys, os; print(os.path.join(os.path.dirname(sys.executable), 'Scripts'))"
    Write-Host "  $scriptsDir" -ForegroundColor Cyan
    Write-Host ""
}
