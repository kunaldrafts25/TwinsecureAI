# Script to run tests with proper PYTHONPATH and coverage

param (
    [switch]$All = $false,
    [switch]$Health = $false,
    [switch]$Auth = $false,
    [switch]$Coverage = $false,
    [switch]$Verbose = $false
)

Write-Host "Setting up environment for tests..." -ForegroundColor Green

# Set PYTHONPATH environment variable
$env:PYTHONPATH = "$PWD"
Write-Host "PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Yellow

# Change to backend directory
cd backend

# Build the test command
$testCommand = "python -m pytest"

# Add test targets
if ($Health) {
    $testCommand += " tests/test_health.py"
}
elseif ($Auth) {
    $testCommand += " tests/test_api_auth.py"
}
elseif ($All) {
    $testCommand += " tests/"
}
else {
    # Default to health test if no specific test is specified
    $testCommand += " tests/test_health.py"
}

# Add verbose flag if requested
if ($Verbose) {
    $testCommand += " -v"
}

# Add coverage flags if requested
if ($Coverage) {
    $testCommand += " --cov=app --cov-report=xml --cov-report=term"
}

# Run the tests
Write-Host "Running tests with command: $testCommand" -ForegroundColor Green
Invoke-Expression $testCommand

# Return to the root directory
cd ..

Write-Host "Tests completed!" -ForegroundColor Green
