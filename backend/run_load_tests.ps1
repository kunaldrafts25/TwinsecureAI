# Run load tests with Locust
# Usage: .\run_load_tests.ps1 [options]
# Options:
#   -u: Number of users (default: 10)
#   -r: Spawn rate (default: 1)
#   -t: Run time (default: 1m)
#   -h: Host (default: http://localhost:8000)
#   -headless: Run in headless mode
#   -tag: Filter by tag

param(
    [int]$u = 10,
    [int]$r = 1,
    [string]$t = "1m",
    [string]$h = "http://localhost:8000",
    [switch]$headless,
    [string]$tag
)

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Build the command
$cmd = "locust -f tests\locustfile.py"

# Add headless mode
if ($headless) {
    $cmd += " --headless"
}

# Add users and spawn rate
$cmd += " -u $u -r $r"

# Add run time if in headless mode
if ($headless) {
    $cmd += " --run-time $t"
}

# Add host
$cmd += " --host $h"

# Add tag filter
if ($tag) {
    $cmd += " --tags $tag"
}

# Run the command
Write-Host "Running: $cmd"
Invoke-Expression $cmd
