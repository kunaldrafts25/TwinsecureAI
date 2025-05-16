# Comprehensive cleanup script for TwinSecure project
Write-Output "Starting comprehensive cleanup process..."

# Function to safely remove a directory or file
function Remove-SafeItem {
    param (
        [string]$Path
    )
    
    if (Test-Path $Path) {
        Write-Output "Removing $Path..."
        try {
            Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
            Write-Output "Successfully removed $Path"
        }
        catch {
            Write-Output "Failed to remove $Path"
        }
    }
    else {
        Write-Output "$Path does not exist, skipping..."
    }
}

# Remove Python cache files
Write-Output "Removing Python cache files..."
Get-ChildItem -Path "." -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
    Remove-SafeItem -Path $_.FullName
}
Get-ChildItem -Path "." -Recurse -Directory -Filter ".pytest_cache" | ForEach-Object {
    Remove-SafeItem -Path $_.FullName
}

# Remove test coverage files
Write-Output "Removing test coverage files..."
Remove-SafeItem -Path "backend\.coverage"
Remove-SafeItem -Path "backend\coverage_html_report"

# Remove frontend build artifacts
Write-Output "Removing frontend build artifacts..."
Remove-SafeItem -Path "frontend\dist"
Remove-SafeItem -Path "node_modules"

# Remove duplicate files
Write-Output "Removing duplicate files..."
Remove-SafeItem -Path "backend\docker-compose.yml"
Remove-SafeItem -Path "frontend\vite.config.js"

# Remove unnecessary files
Write-Output "Removing unnecessary files..."
Remove-SafeItem -Path "frontend\direct_commands.txt"
Remove-SafeItem -Path "frontend\test_commands.txt"
Remove-SafeItem -Path "frontend\run_specific_test.bat"
Remove-SafeItem -Path "frontend\run_specific_test.sh"
Remove-SafeItem -Path "backend\.gitignore"

# Move test_validation.py to tests directory
Write-Output "Organizing test files..."
if (Test-Path "backend\test_validation.py") {
    if (!(Test-Path "backend\tests")) {
        New-Item -Path "backend\tests" -ItemType Directory -Force
    }
    
    if (Test-Path "backend\tests\test_validation.py") {
        Remove-SafeItem -Path "backend\test_validation.py"
    }
    else {
        try {
            Move-Item -Path "backend\test_validation.py" -Destination "backend\tests\" -Force
            Write-Output "Moved test_validation.py to tests directory"
        }
        catch {
            Write-Output "Failed to move test_validation.py"
        }
    }
}

# Rename Dockerfile.new to Dockerfile in frontend
Write-Output "Organizing Docker files..."
if (Test-Path "frontend\Dockerfile.new") {
    if (Test-Path "frontend\Dockerfile") {
        Remove-SafeItem -Path "frontend\Dockerfile"
    }
    
    try {
        Move-Item -Path "frontend\Dockerfile.new" -Destination "frontend\Dockerfile" -Force
        Write-Output "Renamed Dockerfile.new to Dockerfile"
    }
    catch {
        Write-Output "Failed to rename Dockerfile.new"
    }
}

# Clean up temporary scripts
Write-Output "Cleaning up temporary scripts..."
Remove-SafeItem -Path "cleanup.ps1"
Remove-SafeItem -Path "cleanup_simple.ps1"

Write-Output "Comprehensive cleanup process completed!"
