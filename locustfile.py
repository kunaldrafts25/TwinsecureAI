"""
Locust load testing file for TwinSecure API.
This file defines user behaviors for load testing the TwinSecure API.
"""

from locust import HttpUser, task, between, tag
import json
import random


class TwinSecureUser(HttpUser):
    """
    Simulates a user of the TwinSecure API.
    """
    # Wait between 1 and 3 seconds between tasks
    wait_time = between(1, 3)
    
    # Store the authentication token
    token = None
    
    def on_start(self):
        """
        Initialize the user by attempting to log in.
        """
        # Try to log in to get a token
        response = self.client.post(
            "/api/v1/auth/login",
            data={"username": "admin@example.com", "password": "admin123"}
        )
        
        # If login successful, store the token
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            if self.token:
                # Set the Authorization header for future requests
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @tag("health")
    @task(3)
    def health_check(self):
        """
        Check the health endpoints.
        """
        self.client.get("/health")
        self.client.get("/api/v1/system/health")
    
    @tag("auth")
    @task(2)
    def login(self):
        """
        Test the login endpoint.
        """
        self.client.post(
            "/api/v1/auth/login",
            data={"username": "admin@example.com", "password": "admin123"}
        )
    
    @tag("alerts")
    @task(1)
    def get_alerts(self):
        """
        Get the list of alerts.
        """
        self.client.get("/api/v1/alerts/")
    
    @tag("alerts")
    @task(1)
    def create_alert(self):
        """
        Create a new alert.
        """
        # Generate random alert data
        severity_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        status_options = ["NEW", "INVESTIGATING", "RESOLVED", "FALSE_POSITIVE"]
        
        alert_data = {
            "title": f"Test Alert {random.randint(1000, 9999)}",
            "severity": random.choice(severity_levels),
            "status": random.choice(status_options),
            "source_ip": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "description": "Test alert from load test",
            "tags": ["test", "load-test", "automated"]
        }
        
        self.client.post(
            "/api/v1/alerts/",
            json=alert_data
        )
    
    @tag("users")
    @task(1)
    def get_users(self):
        """
        Get the list of users.
        """
        self.client.get("/api/v1/users/")
    
    @tag("users")
    @task(1)
    def get_user_me(self):
        """
        Get the current user's profile.
        """
        self.client.get("/api/v1/users/me")
    
    @tag("reports")
    @task(1)
    def get_reports(self):
        """
        Get the list of reports.
        """
        self.client.get("/api/v1/reports/")
    
    @tag("honeypot")
    @task(1)
    def get_honeypot(self):
        """
        Get honeypot data.
        """
        self.client.get("/api/v1/honeypot/")


class AdminUser(TwinSecureUser):
    """
    Simulates an admin user with more privileges.
    """
    # Admin users perform more administrative tasks
    
    @tag("admin")
    @task(2)
    def create_user(self):
        """
        Create a new user (admin only).
        """
        # Generate a random user
        user_id = random.randint(1000, 9999)
        user_data = {
            "email": f"test{user_id}@example.com",
            "password": "StrongPassword123!",
            "full_name": f"Test User {user_id}",
            "role": "VIEWER"
        }
        
        self.client.post(
            "/api/v1/users/",
            json=user_data
        )
    
    @tag("admin")
    @task(1)
    def get_system_metrics(self):
        """
        Get system metrics (admin only).
        """
        self.client.get("/api/v1/system/metrics")
