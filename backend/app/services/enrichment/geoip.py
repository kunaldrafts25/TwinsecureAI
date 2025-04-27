import geoip2.database
import geoip2.errors
from app.core.config import settings, logger
from typing import Optional, Dict, Any
import os
from functools import lru_cache # Add cache for performance

# --- Global GeoIP Reader ---
# Initialize the reader once when the module is loaded.
geoip_reader = None
if settings.MAXMIND_DB_PATH:
    if os.path.exists(settings.MAXMIND_DB_PATH):
        try:
            # MODE_MMAP_EXT is generally fastest if C extension available
            # MODE_AUTO tries MMAP_EXT, then MMAP, then MEMORY
            geoip_reader = geoip2.database.Reader(settings.MAXMIND_DB_PATH, mode=geoip2.database.MODE_AUTO)
            logger.info(f"GeoIP2 database loaded successfully from: {settings.MAXMIND_DB_PATH} using mode: {geoip_reader.mode_name}")
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