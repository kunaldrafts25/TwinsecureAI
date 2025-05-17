# Script to run load tests using Docker Compose

param (
    [switch]$Headless = $false,
    [int]$Users = 10,
    [int]$SpawnRate = 1,
    [int]$Duration = 30
)

Write-Host "Starting TwinSecure load testing with Docker Compose..." -ForegroundColor Green

# Check if locustfile.py exists
if (-not (Test-Path "locustfile.py")) {
    Write-Host "locustfile.py not found. Creating it..." -ForegroundColor Yellow
    # The script will create it automatically
}

# Start the containers
Write-Host "Starting Docker containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.load-test.yml up -d

# Wait for the backend to be ready
Write-Host "Waiting for backend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

if ($Headless) {
    # Run Locust in headless mode
    Write-Host "Running Locust in headless mode..." -ForegroundColor Yellow
    Write-Host "Users: $Users, Spawn Rate: $SpawnRate, Duration: $Duration seconds" -ForegroundColor Yellow
    
    docker exec twinsecure_locust locust --headless -u $Users -r $SpawnRate -t ${Duration}s --csv=load_test_results
    
    # Copy the results from the container
    Write-Host "Copying results from container..." -ForegroundColor Yellow
    docker cp twinsecure_locust:/home/locust/load_test_results_stats.csv .
    docker cp twinsecure_locust:/home/locust/load_test_results_stats_history.csv .
    docker cp twinsecure_locust:/home/locust/load_test_results_failures.csv .
    
    Write-Host "Load test completed. Results saved to load_test_results_*.csv" -ForegroundColor Green
} else {
    # Run Locust in web mode
    Write-Host "Locust web interface is available at http://localhost:8089" -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop the containers when done" -ForegroundColor Yellow
    
    try {
        # Open the browser
        Start-Process "http://localhost:8089"
        
        # Wait for user to press Ctrl+C
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } finally {
        # Stop the containers when done
        Write-Host "Stopping Docker containers..." -ForegroundColor Yellow
        docker-compose -f docker-compose.load-test.yml down
    }
}
