# Script to run the health check test with proper environment setup

Write-Host "Setting up environment for health check test..." -ForegroundColor Green

# Set PYTHONPATH environment variable
$env:PYTHONPATH = "$PWD"
Write-Host "PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Yellow

# Set environment variables for testing
$env:DOTENV_FILE = ".env.test"
Write-Host "Using test environment file: $env:DOTENV_FILE" -ForegroundColor Yellow

# Change to backend directory
cd backend

# Run the health check test
Write-Host "Running health check test..." -ForegroundColor Yellow
python -m pytest tests/test_health.py -v

# Return to the root directory
cd ..

Write-Host "Health check test completed!" -ForegroundColor Green
