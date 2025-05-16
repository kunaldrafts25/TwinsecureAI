# TwinSecure Setup Script
# This script helps set up the TwinSecure environment

param (
    [switch]$WithML = $false,
    [switch]$DevMode = $false,
    [switch]$Force = $false
)

# Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Function to check if Python is installed
function Test-PythonInstalled {
    try {
        $pythonVersion = python --version
        Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
        return $false
    }
}

# Function to check if Docker is installed
function Test-DockerInstalled {
    try {
        $dockerVersion = docker --version
        Write-Host "Found Docker: $dockerVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Docker is not installed or not in PATH" -ForegroundColor Red
        return $false
    }
}

# Function to create a virtual environment
function Create-VirtualEnv {
    if (Test-Path "venv") {
        if ($Force) {
            Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
            Remove-Item -Recurse -Force "venv"
        }
        else {
            Write-Host "Virtual environment already exists. Use -Force to recreate it." -ForegroundColor Yellow
            return
        }
    }
    
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
}

# Function to install dependencies
function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    
    # Activate virtual environment
    if ($PSVersionTable.PSVersion.Major -ge 6) {
        # PowerShell Core (6+)
        & ./venv/bin/Activate.ps1
    }
    else {
        # Windows PowerShell
        & ./venv/Scripts/Activate.ps1
    }
    
    # Upgrade pip, setuptools, and wheel
    python -m pip install --upgrade pip setuptools wheel
    
    # Install backend dependencies
    Set-Location backend
    pip install -r requirements.txt
    
    # Install ML dependencies if requested
    if ($WithML) {
        Write-Host "Installing ML dependencies..." -ForegroundColor Yellow
        pip install -r requirements-ml.txt
    }
    
    # Install development dependencies if requested
    if ($DevMode) {
        Write-Host "Installing development dependencies..." -ForegroundColor Yellow
        pip install black flake8 isort pytest pytest-asyncio pytest-cov
    }
    
    Set-Location ..
    
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
}

# Function to set up the database
function Setup-Database {
    Write-Host "Setting up the database..." -ForegroundColor Yellow
    
    # Check if PostgreSQL is running in Docker
    $pgContainer = docker ps -q -f "name=twinsecure_db"
    
    if (-not $pgContainer) {
        Write-Host "Starting PostgreSQL container..." -ForegroundColor Yellow
        docker-compose up -d db
        
        # Wait for PostgreSQL to start
        Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
    
    # Run database migrations
    Set-Location backend
    
    # Activate virtual environment
    if ($PSVersionTable.PSVersion.Major -ge 6) {
        # PowerShell Core (6+)
        & ../venv/bin/Activate.ps1
    }
    else {
        # Windows PowerShell
        & ../venv/Scripts/Activate.ps1
    }
    
    # Run Alembic migrations
    Write-Host "Running database migrations..." -ForegroundColor Yellow
    alembic upgrade head
    
    Set-Location ..
    
    Write-Host "Database setup completed successfully" -ForegroundColor Green
}

# Main script
Write-Host "TwinSecure Setup Script" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# Check prerequisites
$pythonInstalled = Test-PythonInstalled
$dockerInstalled = Test-DockerInstalled

if (-not $pythonInstalled) {
    Write-Host "Please install Python 3.10+ and try again" -ForegroundColor Red
    exit 1
}

if (-not $dockerInstalled) {
    Write-Host "Docker is not installed. Database setup will be skipped." -ForegroundColor Yellow
    $setupDb = $false
}
else {
    $setupDb = $true
}

# Create virtual environment
Create-VirtualEnv

# Install dependencies
Install-Dependencies

# Set up database if Docker is available
if ($setupDb) {
    Setup-Database
}

Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "To activate the virtual environment, run:" -ForegroundColor Yellow
if ($PSVersionTable.PSVersion.Major -ge 6) {
    Write-Host "  ./venv/bin/Activate.ps1" -ForegroundColor White
}
else {
    Write-Host "  ./venv/Scripts/Activate.ps1" -ForegroundColor White
}

Write-Host "To start the application, run:" -ForegroundColor Yellow
Write-Host "  docker-compose up" -ForegroundColor White
