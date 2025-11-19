"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

License management for application authorization.
"""

from app.core.config import logger


class LicenseManager:
    """License manager for application authorization."""
    
    def __init__(self):
        """Initialize the license manager."""
        self._authorized = True  # Default to authorized for development
        logger.info("License manager initialized")
    
    def is_authorized(self) -> bool:
        """
        Check if the application is authorized to run.
        
        Returns:
            True if authorized, False otherwise
        """
        return self._authorized
    
    def get_license_status(self) -> dict:
        """
        Get the current license status.
        
        Returns:
            Dictionary with license status information
        """
        return {
            "status": "valid" if self._authorized else "invalid",
            "type": "development",
            "expires_at": None,
        }


# Global license manager instance
license_manager = LicenseManager()




