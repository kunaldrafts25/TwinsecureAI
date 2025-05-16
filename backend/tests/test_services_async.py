"""
Tests for service modules.
These tests focus on improving code coverage for service modules.
"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import os
import tempfile
import asyncio

# Import services to test
from app.services.alerting.client import AlertingClient
from app.services.alerting.email import EmailAlerter
from app.services.alerting.slack import SlackAlerter
from app.services.alerting.discord import DiscordAlerter
from app.services.enrichment.abuseipdb import AbuseIPDBClient
from app.services.enrichment.geoip import GeoIPClient
from app.services.rate_limiter import RateLimiter
from app.services.validation import validate_ip, validate_email, validate_hostname

class TestAlertingClient:
    """Tests for the AlertingClient class."""

    def test_init(self):
        """Test initialization of AlertingClient."""
        client = AlertingClient(
            email_config={"enabled": True, "smtp_server": "smtp.example.com"},
            slack_config={"enabled": True, "webhook_url": "https://hooks.slack.com/services/xxx"},
            discord_config={"enabled": True, "webhook_url": "https://discord.com/api/webhooks/xxx"}
        )
        assert client.email_alerter is not None
        assert client.slack_alerter is not None
        assert client.discord_alerter is not None

    @pytest.mark.asyncio
    async def test_send_alert(self):
        """Test sending alerts through all channels."""
        # Configure mocks
        with patch('app.services.alerting.email.EmailAlerter.send_alert', new_callable=AsyncMock) as mock_email, \
             patch('app.services.alerting.slack.SlackAlerter.send_alert', new_callable=AsyncMock) as mock_slack, \
             patch('app.services.alerting.discord.DiscordAlerter.send_alert', new_callable=AsyncMock) as mock_discord:

            mock_email.return_value = True
            mock_slack.return_value = True
            mock_discord.return_value = True

            # Create client with all alerters enabled
            client = AlertingClient(
                email_config={"enabled": True, "smtp_server": "smtp.example.com"},
                slack_config={"enabled": True, "webhook_url": "https://hooks.slack.com/services/xxx"},
                discord_config={"enabled": True, "webhook_url": "https://discord.com/api/webhooks/xxx"}
            )

            # Send alert
            alert_data = {
                "id": "123",
                "title": "Test Alert",
                "severity": "HIGH",
                "description": "This is a test alert"
            }
            result = await client.send_alert(alert_data)

            # Verify all alerters were called
            assert result["email"] == True
            assert result["slack"] == True
            assert result["discord"] == True
            mock_email.assert_called_once()
            mock_slack.assert_called_once()
            mock_discord.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_alert_email_only(self):
        """Test sending alerts through email only."""
        # Configure mock
        with patch('app.services.alerting.email.EmailAlerter.send_alert', new_callable=AsyncMock) as mock_email:
            mock_email.return_value = True

            # Create client with only email enabled
            client = AlertingClient(
                email_config={"enabled": True, "smtp_server": "smtp.example.com"},
                slack_config={"enabled": False},
                discord_config={"enabled": False}
            )

            # Send alert
            alert_data = {
                "id": "123",
                "title": "Test Alert",
                "severity": "HIGH",
                "description": "This is a test alert"
            }
            result = await client.send_alert(alert_data)

            # Verify only email alerter was called
            assert result["email"] == True
            assert "slack" not in result
            assert "discord" not in result
            mock_email.assert_called_once()

class TestEmailAlerter:
    """Tests for the EmailAlerter class."""

    @pytest.mark.asyncio
    async def test_send_alert(self):
        """Test sending an alert via email."""
        # Create email alerter
        alerter = EmailAlerter(
            smtp_server="smtp.example.com",
            smtp_port=587,
            username="user",
            password="pass",
            from_email="alerts@example.com",
            to_emails=["admin@example.com"]
        )

        # Patch the _send_email method to avoid actual SMTP operations
        with patch.object(alerter, '_send_email', new_callable=AsyncMock) as mock_send_email:
            # Configure the mock to return None (success)
            mock_send_email.return_value = None

            # Send alert
            alert_data = {
                "id": "123",
                "title": "Test Alert",
                "severity": "HIGH",
                "description": "This is a test alert"
            }
            result = await alerter.send_alert(alert_data)

            # Verify result
            assert result == True

            # Verify _send_email was called with the right parameters
            mock_send_email.assert_called_once()
            # Check that the first argument to _send_email contains the alert title
            args, _ = mock_send_email.call_args
            assert "Test Alert" in args[0]  # Subject should contain the title

class TestSlackAlerter:
    """Tests for the SlackAlerter class."""

    @pytest.mark.asyncio
    async def test_send_alert(self):
        """Test sending an alert via Slack."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        # Create a mock for the AsyncClient.post method
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        # Patch httpx.AsyncClient to return our mock
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Create Slack alerter
            alerter = SlackAlerter(webhook_url="https://hooks.slack.com/services/xxx")

            # Send alert
            alert_data = {
                "id": "123",
                "title": "Test Alert",
                "severity": "HIGH",
                "description": "This is a test alert"
            }
            result = await alerter.send_alert(alert_data)

            # Verify result
            assert result == True
            mock_client.post.assert_called_once()

            # Verify the payload contains the alert data
            args, kwargs = mock_client.post.call_args
            assert alerter.webhook_url == args[0]
            assert "blocks" in kwargs["json"]

class TestDiscordAlerter:
    """Tests for the DiscordAlerter class."""

    @pytest.mark.asyncio
    async def test_send_alert(self):
        """Test sending an alert via Discord."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 204  # Discord returns 204 on success
        mock_response.raise_for_status = MagicMock()

        # Create a mock for the AsyncClient.post method
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        # Patch httpx.AsyncClient to return our mock
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Create Discord alerter
            alerter = DiscordAlerter(webhook_url="https://discord.com/api/webhooks/xxx")

            # Send alert
            alert_data = {
                "id": "123",
                "title": "Test Alert",
                "severity": "HIGH",
                "description": "This is a test alert"
            }
            result = await alerter.send_alert(alert_data)

            # Verify result
            assert result == True
            mock_client.post.assert_called_once()

            # Verify the payload contains the alert data
            args, kwargs = mock_client.post.call_args
            assert alerter.webhook_url == args[0]
            assert "embeds" in kwargs["json"]

class TestAbuseIPDBClient:
    """Tests for the AbuseIPDBClient class."""

    @pytest.mark.asyncio
    async def test_check_ip(self):
        """Test checking an IP with AbuseIPDB."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={
            "data": {
                "ipAddress": "192.168.1.1",
                "abuseConfidenceScore": 80,
                "countryCode": "CN",
                "usageType": "Data Center/Web Hosting/Transit",
                "isp": "Example ISP",
                "domain": "example.com",
                "totalReports": 25
            }
        })

        # Create a mock for the AsyncClient.get method
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        # Patch httpx.AsyncClient to return our mock
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Create AbuseIPDB client
            client = AbuseIPDBClient(api_key="test_key")

            # Check IP
            result = await client.check_ip("192.168.1.1")

            # Verify result
            assert result is not None
            assert result["abuseConfidenceScore"] == 80
            assert result["countryCode"] == "CN"
            mock_client.get.assert_called_once()

            # Verify the request parameters
            args, kwargs = mock_client.get.call_args
            assert client.api_url == args[0]
            assert "ipAddress" in kwargs["params"]
            assert kwargs["params"]["ipAddress"] == "192.168.1.1"

class TestGeoIPClient:
    """Tests for the GeoIPClient class."""

    @pytest.mark.asyncio
    async def test_lookup_ip(self):
        """Test looking up an IP with GeoIP service."""
        # Create a mock for the _lookup_ip_online method
        with patch.object(GeoIPClient, '_lookup_ip_online', new_callable=AsyncMock) as mock_lookup:
            # Configure the mock to return a test result
            mock_result = {
                "ip": "192.168.1.1",
                "country_code": "US",
                "country_name": "United States",
                "city": "New York",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
            mock_lookup.return_value = mock_result

            # Create GeoIP client with no database path to force online lookup
            client = GeoIPClient(api_key="test_key", db_path=None)

            # Lookup IP
            result = await client.lookup_ip("192.168.1.1")

            # Verify result
            assert result is not None
            assert result["country_code"] == "US"
            assert result["city"] == "New York"
            mock_lookup.assert_called_once_with("192.168.1.1")

class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_rate_limiter(self):
        """Test rate limiting functionality."""
        # Create rate limiter with 2 requests per second
        limiter = RateLimiter(max_requests=2, time_window=1)

        # First two requests should be allowed
        assert await limiter.check_rate_limit("test_key") == True
        assert await limiter.check_rate_limit("test_key") == True

        # Third request should be rate limited
        assert await limiter.check_rate_limit("test_key") == False

        # Different key should be allowed
        assert await limiter.check_rate_limit("different_key") == True

        # Test get_remaining_requests
        assert limiter.get_remaining_requests("test_key") == 0
        assert limiter.get_remaining_requests("different_key") == 1
        assert limiter.get_remaining_requests("new_key") == 2

        # Test reset
        limiter.reset("test_key")
        assert await limiter.check_rate_limit("test_key") == True

class TestValidation:
    """Tests for validation functions."""

    def test_validate_ip(self):
        """Test IP validation."""
        # Valid IPs
        assert validate_ip("192.168.1.1") == True
        assert validate_ip("10.0.0.1") == True
        assert validate_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == True

        # Invalid IPs
        assert validate_ip("256.256.256.256") == False
        assert validate_ip("not_an_ip") == False
        assert validate_ip("") == False

    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert validate_email("user@example.com") == True
        assert validate_email("user.name+tag@example.co.uk") == True

        # Invalid emails
        assert validate_email("not_an_email") == False
        assert validate_email("@example.com") == False
        assert validate_email("user@") == False
        assert validate_email("") == False

    def test_validate_hostname(self):
        """Test hostname validation."""
        # Valid hostnames
        assert validate_hostname("example.com") == True
        assert validate_hostname("sub.example.com") == True
        assert validate_hostname("example") == True

        # Invalid hostnames
        assert validate_hostname("example..com") == False
        assert validate_hostname("-example.com") == False
        assert validate_hostname("") == False
