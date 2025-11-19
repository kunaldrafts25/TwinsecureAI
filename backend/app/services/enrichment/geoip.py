"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

GeoIP location lookup service using MaxMind database.
"""

import asyncio
import logging
import os
from functools import lru_cache

import geoip2.database
import geoip2.errors
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeoIPClient:
    """
    Client for IP geolocation lookups using MaxMind GeoIP2 database.
    Falls back to ipapi.co if local database is unavailable.
    """
    
    def __init__(self, db_path: str | None = None):
        """
        Initialize the GeoIP client.
        
        Args:
            db_path: Path to MaxMind GeoIP2 database file
        """
        self.db_path = db_path or self._get_db_path()
        self.reader = None
        
        # Initialize database reader if path exists
        if self.db_path and os.path.exists(self.db_path):
            try:
                self.reader = geoip2.database.Reader(
                    self.db_path,
                    mode=geoip2.database.MODE_AUTO
                )
                logger.info(f"GeoIP database loaded from {self.db_path}")
            except Exception as e:
                logger.error(f"Failed to load GeoIP database: {e}")
        else:
            logger.warning("GeoIP database not configured or file not found")
    
    def _get_db_path(self) -> str | None:
        """Get MaxMind database path from settings or environment."""
        # Check settings first
        if hasattr(settings, "MAXMIND_DB_PATH") and settings.MAXMIND_DB_PATH:
            return str(settings.MAXMIND_DB_PATH)
        
        # Check nested config
        if hasattr(settings, "geoip2") and hasattr(settings.geoip2, "db_path"):
            return settings.geoip2.db_path
        
        # Check environment variable
        return os.getenv("MAXMIND_DB_PATH")
    
    async def lookup_ip(self, ip_address: str) -> dict[str, any] | None:
        """
        Look up geolocation information for an IP address.
        Tries local database first, falls back to online API.
        
        Args:
            ip_address: IP address to look up
            
        Returns:
            Dictionary containing geolocation data or None
        """
        # Try local database first
        if self.reader:
            result = await self._lookup_local(ip_address)
            if result:
                return result
        
        # Fall back to online API
        return await self._lookup_online(ip_address)
    
    async def _lookup_local(self, ip_address: str) -> dict[str, any] | None:
        """
        Look up IP in local MaxMind database.
        
        Args:
            ip_address: IP address to look up
            
        Returns:
            Dictionary with geolocation data or None
        """
        if not self.reader:
            return None
        
        try:
            # Run blocking database lookup in thread pool
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                self.reader.city,
                ip_address
            )
            
            # Build response dict
            data = {
                "ip": ip_address,
                "country_iso": response.country.iso_code,
                "country": response.country.name,
                "city": response.city.name,
                "postal_code": response.postal.code,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "timezone": response.location.time_zone,
            }
            
            # Filter out None values
            return {k: v for k, v in data.items() if v is not None}
        
        except geoip2.errors.AddressNotFoundError:
            logger.debug(f"IP {ip_address} not found in GeoIP database")
            return None
        
        except ValueError as e:
            logger.warning(f"Invalid IP address {ip_address}: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Error looking up {ip_address} in GeoIP database: {e}")
            return None
    
    async def _lookup_online(self, ip_address: str) -> dict[str, any] | None:
        """
        Look up IP using ipapi.co free API as fallback.
        
        Args:
            ip_address: IP address to look up
            
        Returns:
            Dictionary with geolocation data or None
        """
        try:
            url = f"https://ipapi.co/{ip_address}/json/"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f"ipapi.co rate limit exceeded for {ip_address}")
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                # Check for error response
                if "error" in data:
                    logger.warning(
                        f"ipapi.co returned error for {ip_address}: {data.get('reason')}"
                    )
                    return None
                
                # Normalize field names to match local format
                return {
                    "ip": ip_address,
                    "country_iso": data.get("country_code"),
                    "country": data.get("country_name"),
                    "city": data.get("city"),
                    "postal_code": data.get("postal"),
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "timezone": data.get("timezone"),
                }
        
        except httpx.TimeoutException:
            logger.error(f"Timeout looking up {ip_address} with ipapi.co")
            return None
        
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} looking up {ip_address}: "
                f"{e.response.text}"
            )
            return None
        
        except Exception as e:
            logger.error(f"Error looking up {ip_address} with ipapi.co: {e}")
            return None
    
    def close(self) -> None:
        """Close the GeoIP database reader."""
        if self.reader:
            try:
                self.reader.close()
                logger.info("GeoIP database reader closed")
            except Exception as e:
                logger.error(f"Error closing GeoIP reader: {e}")
            finally:
                self.reader = None


# Global singleton instance
_geoip_client: GeoIPClient | None = None


def get_geoip_client() -> GeoIPClient:
    """Get or create the global GeoIP client instance."""
    global _geoip_client
    
    if _geoip_client is None:
        _geoip_client = GeoIPClient()
    
    return _geoip_client


@lru_cache(maxsize=1024)
def _lookup_sync(ip_address: str) -> dict[str, any] | None:
    """Cached synchronous GeoIP lookup (for use with thread pool)."""
    client = get_geoip_client()
    
    if not client.reader:
        return None
    
    try:
        response = client.reader.city(ip_address)
        
        data = {
            "country_iso": response.country.iso_code,
            "country": response.country.name,
            "city": response.city.name,
            "postal_code": response.postal.code,
            "latitude": response.location.latitude,
            "longitude": response.location.longitude,
            "timezone": response.location.time_zone,
        }
        
        return {k: v for k, v in data.items() if v is not None}
    
    except geoip2.errors.AddressNotFoundError:
        return None
    
    except Exception:
        return None


async def get_ip_location(ip_address: str) -> dict[str, any] | None:
    """
    Convenience function for GeoIP lookup (cached).
    
    Args:
        ip_address: IP address to look up
        
    Returns:
        Dictionary containing geolocation data or None
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _lookup_sync, ip_address)


def close_geoip_reader() -> None:
    """Close the global GeoIP client (call on app shutdown)."""
    global _geoip_client
    
    if _geoip_client:
        _geoip_client.close()
        _geoip_client = None


# Backward compatibility exports
geoip_reader = get_geoip_client()
