import geoip2.database
import geoip2.errors
import logging
import requests
import os
import asyncio
from app.core.config import settings
from typing import Optional, Dict, Any
from functools import lru_cache # Add cache for performance

logger = logging.getLogger(__name__)

class GeoIPClient:
    """Client for IP geolocation lookups."""

    def __init__(self, api_key: Optional[str] = None, db_path: Optional[str] = None):
        """
        Initialize the GeoIP client.

        Args:
            api_key: API key for online geolocation service
            db_path: Path to local MaxMind database file
        """
        self.api_key = api_key
        self.db_path = db_path
        self.reader = None

        # Initialize database reader if path is provided
        if db_path and os.path.exists(db_path):
            try:
                self.reader = geoip2.database.Reader(db_path)
                logger.info(f"GeoIP database loaded from {db_path}")
            except Exception as e:
                logger.error(f"Failed to load GeoIP database: {str(e)}")

    async def lookup_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Look up geolocation information for an IP address.

        Args:
            ip_address: IP address to look up

        Returns:
            Dict containing geolocation information or None if an error occurs
        """
        # Try local database first if available
        if self.reader:
            try:
                result = await self._lookup_ip_local(ip_address)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Error looking up IP {ip_address} in local database: {str(e)}")

        # Fall back to online API if API key is provided
        if self.api_key:
            try:
                return await self._lookup_ip_online(ip_address)
            except Exception as e:
                logger.error(f"Error looking up IP {ip_address} with online API: {str(e)}")

        return None

    async def _lookup_ip_local(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Look up IP address in local MaxMind database.

        Args:
            ip_address: IP address to look up

        Returns:
            Dict containing geolocation information or None if an error occurs
        """
        if not self.reader:
            return None

        try:
            # Run the blocking database lookup in a thread pool
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, self.reader.city, ip_address)

            # Extract relevant information
            return {
                "ip": ip_address,
                "country_code": response.country.iso_code,
                "country_name": response.country.name,
                "city": response.city.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "timezone": response.location.time_zone
            }
        except geoip2.errors.AddressNotFoundError:
            logger.debug(f"IP {ip_address} not found in GeoIP database")
            return None
        except Exception as e:
            logger.error(f"Error looking up IP {ip_address} in GeoIP database: {str(e)}")
            return None

    async def _lookup_ip_online(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Look up IP address using an online API.

        Args:
            ip_address: IP address to look up

        Returns:
            Dict containing geolocation information or None if an error occurs
        """
        try:
            # Use a free IP geolocation API (replace with your preferred service)
            url = f"https://ipapi.co/{ip_address}/json/"

            # Run the blocking HTTP request in a thread pool
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, timeout=5)
            )

            response.raise_for_status()
            data = response.json()

            # Extract relevant information
            return {
                "ip": ip_address,
                "country_code": data.get("country_code"),
                "country_name": data.get("country_name"),
                "city": data.get("city"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "timezone": data.get("timezone")
            }
        except Exception as e:
            logger.error(f"Error looking up IP {ip_address} with online API: {str(e)}")
            return None


# --- Global GeoIP Reader ---
# Initialize the reader once when the module is loaded.
geoip_reader = None
if settings.MAXMIND_DB_PATH:
    if os.path.exists(settings.MAXMIND_DB_PATH):
        try:
            # MODE_AUTO tries MMAP_EXT, then MMAP, then MEMORY
            geoip_reader = geoip2.database.Reader(settings.MAXMIND_DB_PATH, mode=geoip2.database.MODE_AUTO)
            logger.info(f"GeoIP2 database loaded successfully from: {settings.MAXMIND_DB_PATH}")
        except Exception as e:
            logger.error(f"Failed to load GeoIP2 database from {settings.MAXMIND_DB_PATH}: {e}")
            geoip_reader = None
    else:
        logger.error(f"GeoIP2 database file not found at configured path: {settings.MAXMIND_DB_PATH}")
else:
    logger.warning("MaxMind DB path (MAXMIND_DB_PATH) not configured. GeoIP lookups disabled.")


@lru_cache(maxsize=1024) # Cache recent lookups
def _get_geoip_data_sync(ip_address: str) -> Optional[Dict[str, Any]]:
    """Synchronous helper for GeoIP lookup to allow caching."""
    if not geoip_reader:
        return None
    try:
        response = geoip_reader.city(ip_address)
        data = {
            "country_iso": response.country.iso_code,
            "country": response.country.name,
            "city": response.city.name,
            "postal_code": response.postal.code,
            "latitude": response.location.latitude,
            "longitude": response.location.longitude,
            "timezone": response.location.time_zone,
            # Add ASN if using City or Enterprise DB that includes it
            # "asn": response.traits.autonomous_system_number,
            # "asn_org": response.traits.autonomous_system_organization,
        }
        geo_info = {k: v for k, v in data.items() if v is not None}
        logger.debug(f"GeoIP lookup successful for {ip_address}: {geo_info.get('city')}, {geo_info.get('country')}")
        return geo_info
    except geoip2.errors.AddressNotFoundError:
        logger.debug(f"GeoIP lookup failed for {ip_address}: Address not found in database.")
        return None
    except ValueError as e:
         logger.warning(f"GeoIP lookup failed for {ip_address}: Invalid IP address format? Error: {e}")
         return None
    except Exception as e:
        # Log less severe errors less frequently if needed
        logger.error(f"An unexpected error occurred during GeoIP lookup for {ip_address}: {e}")
        return None

async def get_geoip_data(ip_address: str) -> Optional[Dict[str, Any]]:
    """
    Performs a GeoIP lookup using the loaded MaxMind DB, running the sync lookup in a thread.

    Args:
        ip_address: The IP address string to look up.

    Returns:
        A dictionary containing GeoIP data or None if lookup fails.
    """
    if not geoip_reader:
        # logger.debug("GeoIP reader not available. Skipping GeoIP lookup.")
        return None
    try:
        # Run the synchronous, cached lookup in a thread pool
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, _get_geoip_data_sync, ip_address)
        return result
    except Exception as e:
         # This catches errors during the async execution itself, not the sync function errors
         logger.error(f"Error running GeoIP lookup in executor for {ip_address}: {e}")
         return None


def close_geoip_reader():
    """Closes the GeoIP database reader if it's open."""
    global geoip_reader
    if geoip_reader:
        try:
            geoip_reader.close()
            logger.info("GeoIP database reader closed.")
        except Exception as e:
            logger.error(f"Error closing GeoIP reader: {e}")
        geoip_reader = None

# Ensure the close function is called on application shutdown
# Add `from app.services.enrichment.geoip import close_geoip_reader` to main.py
# and call `close_geoip_reader()` in the shutdown event handler.