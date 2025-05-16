# Script to run tests with proper PYTHONPATH

Write-Host "Setting up environment for tests..." -ForegroundColor Green

# Set PYTHONPATH environment variable
$env:PYTHONPATH = "$PWD"
Write-Host "PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Yellow

# Change to backend directory
cd backend

# Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
python -m pytest --cov=app --cov-report=term

# Return to the root directory
cd ..

Write-Host "Tests completed!" -ForegroundColor Green
