# TwinSecure Deployment Script
# This script automates the deployment of the TwinSecure platform

param (
    [string]$Environment = "development",
    [switch]$BuildImages = $false,
    [switch]$PullImages = $false,
    [switch]$MigrateDatabase = $true,
    [switch]$LoadFixtures = $false,
    [switch]$BackupDatabase = $true,
    [switch]$Force = $false
)

# Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Set environment-specific variables
$EnvFile = ".env.$Environment"
if (Test-Path $EnvFile) {
    Write-Host "Loading environment variables from $EnvFile" -ForegroundColor Green
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
            Write-Host "Set $key environment variable" -ForegroundColor Gray
        }
    }
}

# Select the appropriate docker-compose file
$ComposeFile = if ($Environment -eq "production") { "docker-compose.prod.yml" } else { "docker-compose.yml" }
Write-Host "Using Docker Compose file: $ComposeFile" -ForegroundColor Green

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        $null = docker info
        return $true
    }
    catch {
        return $false
    }
}

# Function to backup the database
function Backup-Database {
    $BackupDir = "backups"
    if (-not (Test-Path $BackupDir)) {
        New-Item -Path $BackupDir -ItemType Directory | Out-Null
    }
    
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupFile = Join-Path $BackupDir "twinsecure_$Timestamp.sql"
    
    Write-Host "Backing up database to $BackupFile..." -ForegroundColor Yellow
    
    docker-compose -f $ComposeFile exec -T postgres pg_dump -U postgres -d TwinSecure > $BackupFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database backup completed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "Database backup failed" -ForegroundColor Red
        exit 1
    }
}

# Function to migrate the database
function Migrate-Database {
    Write-Host "Running database migrations..." -ForegroundColor Yellow
    
    docker-compose -f $ComposeFile exec -T backend alembic upgrade head
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database migrations completed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "Database migrations failed" -ForegroundColor Red
        exit 1
    }
}

# Function to load fixtures
function Load-Fixtures {
    Write-Host "Loading fixtures..." -ForegroundColor Yellow
    
    docker-compose -f $ComposeFile exec -T backend python -m scripts.load_fixtures
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Fixtures loaded successfully" -ForegroundColor Green
    }
    else {
        Write-Host "Failed to load fixtures" -ForegroundColor Red
        exit 1
    }
}

# Main deployment logic
try {
    # Check if Docker is running
    if (-not (Test-DockerRunning)) {
        Write-Host "Docker is not running. Please start Docker and try again." -ForegroundColor Red
        exit 1
    }
    
    # Check if the compose file exists
    if (-not (Test-Path $ComposeFile)) {
        Write-Host "Docker Compose file not found: $ComposeFile" -ForegroundColor Red
        exit 1
    }
    
    # Build or pull images
    if ($BuildImages) {
        Write-Host "Building Docker images..." -ForegroundColor Yellow
        docker-compose -f $ComposeFile build
    }
    elseif ($PullImages) {
        Write-Host "Pulling Docker images..." -ForegroundColor Yellow
        docker-compose -f $ComposeFile pull
    }
    
    # Check if services are already running
    $RunningContainers = docker-compose -f $ComposeFile ps -q
    if ($RunningContainers -and -not $Force) {
        $Confirm = Read-Host "Services are already running. Do you want to stop and restart them? (y/n)"
        if ($Confirm -ne "y") {
            Write-Host "Deployment aborted" -ForegroundColor Yellow
            exit 0
        }
        
        Write-Host "Stopping running services..." -ForegroundColor Yellow
        docker-compose -f $ComposeFile down
    }
    
    # Start services
    Write-Host "Starting services..." -ForegroundColor Yellow
    docker-compose -f $ComposeFile up -d
    
    # Wait for services to be ready
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Backup database if requested
    if ($BackupDatabase) {
        Backup-Database
    }
    
    # Migrate database if requested
    if ($MigrateDatabase) {
        Migrate-Database
    }
    
    # Load fixtures if requested
    if ($LoadFixtures) {
        Load-Fixtures
    }
    
    # Display service status
    Write-Host "Deployment completed successfully" -ForegroundColor Green
    docker-compose -f $ComposeFile ps
    
    # Display access URLs
    $ApiUrl = if ($Environment -eq "production") { "https://api.twinsecure.example.com" } else { "http://localhost:8000" }
    $WebUrl = if ($Environment -eq "production") { "https://twinsecure.example.com" } else { "http://localhost:5173" }
    
    Write-Host "`nAccess URLs:" -ForegroundColor Cyan
    Write-Host "API: $ApiUrl" -ForegroundColor Cyan
    Write-Host "Web: $WebUrl" -ForegroundColor Cyan
    Write-Host "API Documentation: $ApiUrl/api/v1/docs" -ForegroundColor Cyan
    
    if ($Environment -eq "production") {
        Write-Host "Grafana: https://twinsecure.example.com/grafana" -ForegroundColor Cyan
        Write-Host "Kibana: https://twinsecure.example.com/kibana" -ForegroundColor Cyan
        Write-Host "PgAdmin: https://twinsecure.example.com/pgadmin" -ForegroundColor Cyan
    }
    else {
        Write-Host "Grafana: http://localhost:3001" -ForegroundColor Cyan
        Write-Host "Kibana: http://localhost:5601" -ForegroundColor Cyan
        Write-Host "PgAdmin: http://localhost:5050" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "Deployment failed: $_" -ForegroundColor Red
    exit 1
}
