# Setup database for TwinSecure
# This script creates the TwinSecure database and runs migrations

# Check if PostgreSQL is installed
$pgPath = "C:\Program Files\PostgreSQL\17\bin"
if (-not (Test-Path $pgPath)) {
    Write-Host "PostgreSQL not found at $pgPath" -ForegroundColor Red
    exit 1
}

# Set environment variables
$env:PGPASSWORD = "kUNAL@#$12345"
$dbName = "TwinSecure"
$dbUser = "postgres"

# Check if database exists
Write-Host "Checking if database exists..." -ForegroundColor Cyan
$dbExists = & "$pgPath\psql.exe" -U $dbUser -t -c "SELECT 1 FROM pg_database WHERE datname = '$dbName'"

if (-not $dbExists) {
    Write-Host "Creating database $dbName..." -ForegroundColor Yellow
    & "$pgPath\createdb.exe" -U $dbUser $dbName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database created successfully!" -ForegroundColor Green
    } else {
        Write-Host "Failed to create database!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Database $dbName already exists." -ForegroundColor Green
}

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Cyan
cd backend
if (Test-Path "venv") {
    # Activate virtual environment
    .\venv\Scripts\Activate
} else {
    # Create virtual environment
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate
    
    # Install requirements
    Write-Host "Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Run Alembic migrations
Write-Host "Running Alembic migrations..." -ForegroundColor Cyan
alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database migrations completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to run migrations!" -ForegroundColor Red
    exit 1
}

# Deactivate virtual environment
deactivate

Write-Host "Database setup complete!" -ForegroundColor Green
