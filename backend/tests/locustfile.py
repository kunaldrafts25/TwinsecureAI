"""
Load testing script for TwinSecure API.
Run with: locust -f locustfile.py
"""
import time
import json
import random
from locust import HttpUser, task, between, tag

class TwinSecureUser(HttpUser):
    """
    Simulates a user of the TwinSecure API.
    """
    # Wait between 1 and 5 seconds between tasks
    wait_time = between(1, 5)
    
    # Store the authentication token
    token = None
    
    def on_start(self):
        """
        Log in when the user starts.
        """
        self.login()
    
    def login(self):
        """
        Log in to the API and store the token.
        """
        response = self.client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "password"
            }
        )
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
    
    @tag("health")
    @task(10)  # Higher weight for health check
    def health_check(self):
        """
        Check the health of the API.
        """
        self.client.get("/health")
    
    @tag("system")
    @task(5)
    def system_health(self):
        """
        Check the system health.
        """
        self.client.get("/api/v1/system/health")
    
    @tag("alerts")
    @task(3)
    def get_alerts(self):
        """
        Get all alerts.
        """
        if not self.token:
            self.login()
            
        self.client.get("/api/v1/alerts/")
    
    @tag("alerts")
    @task(1)
    def create_alert(self):
        """
        Create a new alert.
        """
        if not self.token:
            self.login()
            
        alert_types = ["INTRUSION", "MALWARE", "PHISHING", "VULNERABILITY"]
        severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        statuses = ["NEW", "ACKNOWLEDGED", "IN_PROGRESS", "RESOLVED", "CLOSED"]
        
        self.client.post(
            "/api/v1/alerts/",
            json={
                "alert_type": random.choice(alert_types),
                "source_ip": f"192.168.1.{random.randint(1, 255)}",
                "severity": random.choice(severities),
                "status": random.choice(statuses),
                "title": f"Test Alert {random.randint(1, 1000)}",
                "description": "This is a test alert created by the load test."
            }
        )
    
    @tag("users")
    @task(2)
    def get_current_user(self):
        """
        Get the current user.
        """
        if not self.token:
            self.login()
            
        self.client.get("/api/v1/users/me")
    
    @tag("reports")
    @task(1)
    def get_reports(self):
        """
        Get all reports.
        """
        if not self.token:
            self.login()
            
        self.client.get("/api/v1/reports/")
    
    @tag("honeypot")
    @task(1)
    def get_honeypot(self):
        """
        Get honeypot data.
        """
        if not self.token:
            self.login()
            
        self.client.get("/api/v1/honeypot/")


class TwinSecureAdminUser(HttpUser):
    """
    Simulates an admin user of the TwinSecure API.
    """
    # Wait between 2 and 8 seconds between tasks (admins are less frequent)
    wait_time = between(2, 8)
    
    # Store the authentication token
    token = None
    
    def on_start(self):
        """
        Log in when the user starts.
        """
        self.login()
    
    def login(self):
        """
        Log in to the API and store the token.
        """
        response = self.client.post(
            "/api/v1/auth/login",
            data={
                "username": "admin@example.com",
                "password": "password"
            }
        )
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
    
    @tag("users")
    @task(3)
    def get_users(self):
        """
        Get all users (admin only).
        """
        if not self.token:
            self.login()
            
        self.client.get("/api/v1/users/")
    
    @tag("alerts")
    @task(5)
    def get_all_alerts(self):
        """
        Get all alerts (admin sees more).
        """
        if not self.token:
            self.login()
            
        self.client.get("/api/v1/alerts/")
    
    @tag("system")
    @task(2)
    def system_health(self):
        """
        Check the system health.
        """
        self.client.get("/api/v1/system/health")
