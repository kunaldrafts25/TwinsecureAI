# Run tests with coverage
# Usage: .\run_tests.ps1 [options]
# Options:
#   -html: Generate HTML coverage report
#   -xml: Generate XML coverage report
#   -v: Verbose output
#   -k: Filter tests by keyword
#   -m: Filter tests by marker
#   -xvs: Exclude VS Code tests

param(
    [switch]$html,
    [switch]$xml,
    [switch]$v,
    [string]$k,
    [string]$m,
    [switch]$xvs
)

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Build the command
$cmd = "python -m pytest"

# Add coverage
$cmd += " --cov=app"

# Add coverage report formats
if ($html) {
    $cmd += " --cov-report=html"
}
if ($xml) {
    $cmd += " --cov-report=xml"
}

# Always add terminal report
$cmd += " --cov-report=term"

# Add verbose flag
if ($v) {
    $cmd += " -v"
}

# Add keyword filter
if ($k) {
    $cmd += " -k $k"
}

# Add marker filter
if ($m) {
    $cmd += " -m $m"
}

# Exclude VS Code tests
if ($xvs) {
    $cmd += " --ignore=.vscode"
}

# Run the command
Write-Host "Running: $cmd"
Invoke-Expression $cmd

# Open HTML report if generated
if ($html) {
    Write-Host "Opening HTML coverage report..."
    Start-Process "coverage_html_report\index.html"
}
