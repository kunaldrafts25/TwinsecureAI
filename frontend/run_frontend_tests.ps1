# Run frontend tests
# Usage: .\run_frontend_tests.ps1 [options]
# Options:
#   -watch: Run tests in watch mode
#   -coverage: Generate coverage report
#   -ui: Run tests with UI
#   -utils: Run only utility tests
#   -components: Run only component tests
#   -file: Run tests for a specific file

param(
    [switch]$watch,
    [switch]$coverage,
    [switch]$ui,
    [switch]$utils,
    [switch]$components,
    [string]$file
)

# Check if node_modules exists
if (-not (Test-Path -Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Build the command
$cmd = "npx vitest"

if ($watch) {
    # Watch mode
    Write-Host "Running tests in watch mode..." -ForegroundColor Cyan
    $cmd += " watch"
} elseif ($ui) {
    # UI mode
    Write-Host "Running tests with UI..." -ForegroundColor Cyan
    $cmd += " --ui"
} elseif ($coverage) {
    # Coverage mode
    Write-Host "Running tests with coverage..." -ForegroundColor Cyan
    $cmd += " run --coverage"
} else {
    # Run mode
    Write-Host "Running tests..." -ForegroundColor Cyan
    $cmd += " run"
}

# Add specific test targets
if ($utils) {
    Write-Host "Testing utility functions..." -ForegroundColor Cyan
    $cmd += " src/utils"
} elseif ($components) {
    Write-Host "Testing components..." -ForegroundColor Cyan
    $cmd += " src/components"
} elseif ($file) {
    Write-Host "Testing file: $file" -ForegroundColor Cyan
    $cmd += " $file"
}

# Run the command
Invoke-Expression $cmd

# Check the exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "Tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Tests failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
