#!/bin/bash
# Script to run load tests against the backend server

# Default values
USERS=10
DURATION=30
HOST="localhost"
PORT=8000

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --users=*)
      USERS="${1#*=}"
      shift
      ;;
    --duration=*)
      DURATION="${1#*=}"
      shift
      ;;
    --host=*)
      HOST="${1#*=}"
      shift
      ;;
    --port=*)
      PORT="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo -e "\e[32mRunning load tests against TwinSecure backend...\e[0m"
echo -e "\e[33mTarget: http://$HOST:$PORT\e[0m"
echo -e "\e[33mUsers: $USERS\e[0m"
echo -e "\e[33mDuration: $DURATION seconds\e[0m"

# Check if locust is installed
if command -v locust &> /dev/null; then
  echo -e "\e[32mFound Locust: $(locust --version)\e[0m"
else
  echo -e "\e[33mLocust is not installed. Installing...\e[0m"
  pip install locust
fi

# Create a simple locustfile.py if it doesn't exist
LOCUST_FILE="locustfile.py"
if [ ! -f "$LOCUST_FILE" ]; then
  echo -e "\e[33mCreating Locust file: $LOCUST_FILE\e[0m"
  cat > "$LOCUST_FILE" << 'EOF'
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
EOF
fi

# Run the load test
echo -e "\e[32mStarting load test...\e[0m"
locust --host="http://$HOST:$PORT" --headless -u $USERS -r 1 -t ${DURATION}s --csv=load_test_results
