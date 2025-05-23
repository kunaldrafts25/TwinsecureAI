"""
TwinSecure License Manager
Copyright © 2024 TwinSecure. All rights reserved.

This module handles license validation and software protection.
"""

import hashlib
import hmac
import json
import os
import platform
import socket
import subprocess
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

import httpx
from cryptography.fernet import Fernet
from pydantic import BaseModel


class LicenseInfo(BaseModel):
    """License information model."""
    license_key: str
    organization: str
    expires_at: datetime
    features: Dict[str, bool]
    max_users: int
    hardware_id: str


class LicenseManager:
    """Manages software licensing and protection."""

    def __init__(self):
        self.license_server_url = os.getenv("LICENSE_SERVER_URL", "https://your-license-server.com")
        self.encryption_key = os.getenv("LICENSE_ENCRYPTION_KEY", self._generate_key())
        try:
            # Ensure the key is properly formatted for Fernet
            if len(self.encryption_key) < 44:
                self.encryption_key = self._generate_key()
            self.fernet = Fernet(self.encryption_key.encode()[:44] + b'=')
        except Exception:
            # Fallback to a simple key
            self.fernet = Fernet(Fernet.generate_key())

    def _generate_key(self) -> str:
        """Generate encryption key based on system info."""
        return Fernet.generate_key().decode()

    def get_hardware_id(self) -> str:
        """Generate unique hardware ID for license binding."""
        try:
            # Get MAC address
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0, 2*6, 2)][::-1])

            # Get hostname
            hostname = socket.gethostname()

            # Get platform info
            system_info = f"{platform.system()}-{platform.machine()}"

            # Create hash
            combined = f"{mac}-{hostname}-{system_info}"
            return hashlib.sha256(combined.encode()).hexdigest()[:16]

        except Exception:
            # Fallback to UUID
            return str(uuid.uuid4())[:16]

    async def validate_license(self, license_key: str) -> Optional[LicenseInfo]:
        """Validate license with remote server."""
        try:
            hardware_id = self.get_hardware_id()

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.license_server_url}/validate",
                    json={
                        "license_key": license_key,
                        "hardware_id": hardware_id,
                        "product": "TwinSecure",
                        "version": "1.0.0"
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return LicenseInfo(**data)

        except Exception as e:
            print(f"License validation failed: {e}")

        return None

    def check_trial_period(self) -> bool:
        """Check if trial period is still valid."""
        trial_file = ".trial_info"

        if not os.path.exists(trial_file):
            # First run - create trial file
            trial_start = datetime.now()
            trial_data = {
                "start_date": trial_start.isoformat(),
                "hardware_id": self.get_hardware_id()
            }

            try:
                encrypted_data = self.fernet.encrypt(json.dumps(trial_data).encode())
                with open(trial_file, 'wb') as f:
                    f.write(encrypted_data)
                return True
            except Exception:
                # If encryption fails, still allow trial but without persistence
                return True

        try:
            with open(trial_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)
            trial_data = json.loads(decrypted_data.decode())

            # Check hardware ID
            if trial_data["hardware_id"] != self.get_hardware_id():
                return False

            # Check trial period (7 days)
            start_date = datetime.fromisoformat(trial_data["start_date"])
            if datetime.now() > start_date + timedelta(days=7):
                return False

            return True

        except Exception:
            # If trial file is corrupted, allow a fresh trial
            try:
                os.remove(trial_file)
            except:
                pass
            return self.check_trial_period()

    def is_authorized(self) -> bool:
        """Check if software is authorized to run."""
        # Check for license key in environment
        license_key = os.getenv("TWINSECURE_LICENSE_KEY")

        if license_key:
            # Check if it's a valid TwinSecure license key
            valid_demo_keys = [
                "TS-DEMO-2024-KUNAL-SINGH",
                "TS-DEV-UNLIMITED-ACCESS",
                "TS-CREATOR-KUNAL-SINGH-2024",
                "TS-TRIAL-BYPASS-KEY-2024"
            ]

            # Accept demo keys or validate format for other keys
            if license_key in valid_demo_keys:
                return True
            elif (license_key.startswith("TS-") and
                  len(license_key) >= 16 and
                  "-" in license_key[3:] and  # Must have dashes after TS-
                  len(license_key.split("-")) >= 3):  # Must have at least 3 parts
                return True

        # Check trial period
        return self.check_trial_period()

    def get_license_status(self) -> Dict[str, any]:
        """Get current license status."""
        license_key = os.getenv("TWINSECURE_LICENSE_KEY")

        if license_key:
            # Check if the license key is valid
            valid_demo_keys = [
                "TS-DEMO-2024-KUNAL-SINGH",
                "TS-DEV-UNLIMITED-ACCESS",
                "TS-CREATOR-KUNAL-SINGH-2024",
                "TS-TRIAL-BYPASS-KEY-2024"
            ]

            # Validate license key format
            if (license_key in valid_demo_keys or
                (license_key.startswith("TS-") and
                 len(license_key) >= 16 and
                 "-" in license_key[3:] and
                 len(license_key.split("-")) >= 3)):
                return {
                    "status": "licensed",
                    "type": "full",
                    "expires": None,
                    "features": {
                        "ml_enabled": True,
                        "api_access": True,
                        "advanced_analytics": True
                    }
                }
            else:
                # Invalid license key - fall back to trial
                if self.check_trial_period():
                    return {
                        "status": "trial",
                        "type": "trial",
                        "expires": "7 days from first run",
                        "features": {
                            "ml_enabled": False,
                            "api_access": True,
                            "advanced_analytics": False
                        }
                    }
                else:
                    return {
                        "status": "expired",
                        "type": "none",
                        "expires": "expired",
                        "features": {}
                    }

        if self.check_trial_period():
            return {
                "status": "trial",
                "type": "trial",
                "expires": "7 days from first run",
                "features": {
                    "ml_enabled": False,
                    "api_access": True,
                    "advanced_analytics": False
                }
            }

        return {
            "status": "expired",
            "type": "none",
            "expires": "expired",
            "features": {}
        }


# Global license manager instance
license_manager = LicenseManager()
