# List directory structure
Write-Output "Project Structure:"
Write-Output "================="

# Function to list directory contents
function List-Directory {
    param (
        [string]$Path,
        [int]$Level = 0
    )
    
    $indent = "  " * $Level
    
    Get-ChildItem -Path $Path | ForEach-Object {
        if ($_.PSIsContainer) {
            Write-Output "$indent[D] $($_.Name)"
            if ($Level -lt 2) {  # Limit recursion depth
                List-Directory -Path $_.FullName -Level ($Level + 1)
            }
        }
        else {
            Write-Output "$indent[F] $($_.Name)"
        }
    }
}

# List the root directory
List-Directory -Path "."
