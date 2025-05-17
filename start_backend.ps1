# Script to start the backend server for load testing

Write-Host "Starting TwinSecure backend server for load testing..." -ForegroundColor Green

# Set PYTHONPATH environment variable
$env:PYTHONPATH = "$PWD"
Write-Host "PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Yellow

# Set environment variables for testing
$env:DOTENV_FILE = ".env.test"
Write-Host "Using test environment file: $env:DOTENV_FILE" -ForegroundColor Yellow

# Set database to use SQLite instead of PostgreSQL
$env:TEST_DB = "sqlite"
Write-Host "Using SQLite database for testing" -ForegroundColor Yellow

# Change to backend directory
cd backend

# Start the server with uvicorn
Write-Host "Starting uvicorn server on http://localhost:8000..." -ForegroundColor Yellow
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
