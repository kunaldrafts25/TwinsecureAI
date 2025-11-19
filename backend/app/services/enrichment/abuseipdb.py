"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

AbuseIPDB IP reputation checking service.
"""

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AbuseIPDBClient:
    """Client for checking IP addresses against AbuseIPDB API."""
    
    def __init__(
        self,
        api_key: str | None = None,
        api_url: str = "https://api.abuseipdb.com/api/v2/check"
    ):
        """
        Initialize the AbuseIPDB client.
        
        Args:
            api_key: AbuseIPDB API key (defaults to settings)
            api_url: AbuseIPDB API URL
        """
        self.api_key = api_key or settings.ABUSEIPDB_API_KEY
        self.api_url = api_url or settings.ABUSEIPDB_API_URL
    
    async def check_ip(
        self,
        ip_address: str,
        max_age_days: int = 90,
        verbose: bool = True
    ) -> dict[str, any] | None:
        """
        Check an IP address against AbuseIPDB.
        
        Args:
            ip_address: IP address to check
            max_age_days: Maximum age of reports to consider (default: 90)
            verbose: Include detailed information in response
            
        Returns:
            Dictionary containing IP information or None if an error occurs
        """
        if not self.api_key:
            logger.debug("AbuseIPDB API key not configured, skipping check")
            return None
        
        headers = {
            "Accept": "application/json",
            "Key": self.api_key
        }
        
        params = {
            "ipAddress": ip_address,
            "maxAgeInDays": str(max_age_days),
        }
        
        if verbose:
            params["verbose"] = ""  # Empty string enables verbose mode
        
        logger.debug(f"Checking IP {ip_address} with AbuseIPDB")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.api_url,
                    headers=headers,
                    params=params
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(
                        f"AbuseIPDB rate limit exceeded for IP {ip_address}. "
                        "Check API plan or implement retry logic."
                    )
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                # Validate response structure
                if not isinstance(data.get("data"), dict):
                    logger.warning(
                        f"Invalid response format from AbuseIPDB for IP {ip_address}"
                    )
                    return None
                
                return data["data"]
        
        except httpx.TimeoutException:
            logger.error(f"Timeout checking IP {ip_address} with AbuseIPDB")
            return None
        
        except httpx.RequestError as e:
            logger.error(
                f"Request error checking IP {ip_address}: {e.request.url} - {e}"
            )
            return None
        
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} checking IP {ip_address}: "
                f"{e.response.text}"
            )
            return None
        
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing AbuseIPDB response for {ip_address}: {e}")
            return None
        
        except Exception as e:
            logger.exception(
                f"Unexpected error checking IP {ip_address} with AbuseIPDB: {e}"
            )
            return None
    
    async def get_abuse_score(self, ip_address: str) -> int | None:
        """
        Get the abuse confidence score for an IP address.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            Abuse confidence score (0-100) or None if unavailable
        """
        result = await self.check_ip(ip_address, verbose=False)
        
        if not result:
            return None
        
        # Handle whitelisted IPs
        if result.get("isWhitelisted"):
            logger.info(f"IP {ip_address} is whitelisted by AbuseIPDB")
            return 0
        
        # Extract score
        score = result.get("abuseConfidenceScore")
        
        if score is not None:
            logger.info(f"AbuseIPDB score for {ip_address}: {score}")
            return int(score)
        
        logger.warning(
            f"AbuseIPDB response for {ip_address} missing score data"
        )
        return None


# Convenience function for backward compatibility
async def check_ip_reputation(ip_address: str) -> dict[str, Any] | None:
    """
    Check IP reputation using AbuseIPDB (convenience function).
    
    Args:
        ip_address: IP address to check
        
    Returns:
        Dictionary containing IP information or None
    """
    client = AbuseIPDBClient()
    return await client.check_ip(ip_address)
