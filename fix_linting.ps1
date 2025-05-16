# Script to fix linting issues in the TwinSecure codebase

Write-Host "Starting linting fixes..." -ForegroundColor Green

# Install required linting tools
Write-Host "Installing linting tools..." -ForegroundColor Yellow
cd backend
pip install black flake8 isort

# Run black to format code
Write-Host "Running black to format code..." -ForegroundColor Yellow
black app tests

# Run isort to sort imports
Write-Host "Running isort to sort imports..." -ForegroundColor Yellow
isort --profile black app tests

# Check if there are still issues with flake8
Write-Host "Checking for remaining issues with flake8..." -ForegroundColor Yellow
flake8 app tests --count

Write-Host "Linting fixes completed!" -ForegroundColor Green

# Return to the root directory
cd ..
