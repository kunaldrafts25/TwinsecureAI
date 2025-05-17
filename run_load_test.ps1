# Script to run load tests against the backend server

param (
    [int]$Users = 10,
    [int]$Duration = 30,
    [string]$Host = "localhost",
    [int]$Port = 8000
)

Write-Host "Running load tests against TwinSecure backend..." -ForegroundColor Green
Write-Host "Target: http://$Host:$Port" -ForegroundColor Yellow
Write-Host "Users: $Users" -ForegroundColor Yellow
Write-Host "Duration: $Duration seconds" -ForegroundColor Yellow

# Check if locust is installed
try {
    $locustVersion = locust --version
    Write-Host "Found Locust: $locustVersion" -ForegroundColor Green
}
catch {
    Write-Host "Locust is not installed. Installing..." -ForegroundColor Yellow
    pip install locust
}

# Create a simple locustfile.py if it doesn't exist
$locustFile = "locustfile.py"
if (-not (Test-Path $locustFile)) {
    Write-Host "Creating Locust file: $locustFile" -ForegroundColor Yellow
    @"
from locust import HttpUser, task, between

class TwinSecureUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def health_check(self):
        self.client.get("/health")
        self.client.get("/api/v1/system/health")
    
    @task(2)
    def login(self):
        self.client.post("/api/v1/auth/login", 
                        data={"username": "admin@example.com", "password": "admin123"})
    
    @task(1)
    def get_alerts(self):
        self.client.get("/api/v1/alerts/")
    
    @task(1)
    def create_alert(self):
        self.client.post("/api/v1/alerts/", 
                        json={
                            "title": "Test Alert",
                            "severity": "MEDIUM",
                            "status": "NEW",
                            "source_ip": "192.168.1.100",
                            "description": "Test alert from load test"
                        })
    
    @task(1)
    def get_users(self):
        self.client.get("/api/v1/users/")
    
    @task(1)
    def get_user_me(self):
        self.client.get("/api/v1/users/me")
    
    @task(1)
    def get_reports(self):
        self.client.get("/api/v1/reports/")
    
    @task(1)
    def get_honeypot(self):
        self.client.get("/api/v1/honeypot/")
"@ | Out-File -FilePath $locustFile -Encoding utf8
}

# Run the load test
Write-Host "Starting load test..." -ForegroundColor Green
locust --host="http://$Host:$Port" --headless -u $Users -r 1 -t ${Duration}s --csv=load_test_results
