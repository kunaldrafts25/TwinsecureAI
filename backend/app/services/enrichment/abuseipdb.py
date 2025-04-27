import httpx
from app.core.config import settings, logger
from typing import Optional, Dict, Any

async def get_abuseipdb_score(ip_address: str) -> Optional[int]:
    """
    Queries the AbuseIPDB API to get the confidence score for an IP address.

    Args:
        ip_address: The IP address string to check.

    Returns:
        The abuse confidence score (0-100) or None if an error occurs or API key is missing.
    """
    if not settings.ABUSEIPDB_API_KEY:
        logger.debug("AbuseIPDB API key not configured. Skipping IP score check.")
        return None

    headers = {
        'Accept': 'application/json',
        'Key': settings.ABUSEIPDB_API_KEY
    }
    params = {
        'ipAddress': ip_address,
        'maxAgeInDays': '90', # Check reports within the last 90 days
        # 'verbose': '' # Add verbose flag if more details like country are needed from this API
    }
    url = settings.ABUSEIPDB_API_URL

    logger.debug(f"Querying AbuseIPDB for IP: {ip_address}")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=params)

            # Check for rate limiting specifically
            if response.status_code == 429:
                logger.warning(f"AbuseIPDB rate limit exceeded for IP {ip_address}. Check API plan.")
                # Consider adding retry logic with backoff if appropriate
                return None # Or raise a specific exception

            response.raise_for_status() # Raise exceptions for other 4xx/5xx errors

            data = response.json()
            # Check if the 'data' key exists and contains the score
            if isinstance(data.get('data'), dict) and 'abuseConfidenceScore' in data['data']:
                score = data['data']['abuseConfidenceScore']
                logger.info(f"AbuseIPDB score for {ip_address}: {score}")
                return int(score)
            else:
                # Log if IP is whitelisted or no data found
                if isinstance(data.get('data'), dict) and data['data'].get('isWhitelisted'):
                    logger.info(f"IP {ip_address} is whitelisted by AbuseIPDB.")
                    return 0 # Treat whitelisted as 0 score
                else:
                    logger.warning(f"AbuseIPDB response for {ip_address} missing score data or invalid format: {data}")
                    return None # No score found

    except httpx.TimeoutException:
        logger.error(f"Timeout querying AbuseIPDB for {ip_address} at {url}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Error querying AbuseIPDB for {ip_address} (request failed): {e.request.url} - {e}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"Error querying AbuseIPDB for {ip_address} (HTTP status {e.response.status_code}): {e.response.text}")
        return None
    except (ValueError, TypeError) as e: # Catch JSON decoding errors or type issues
         logger.error(f"Error processing AbuseIPDB response for {ip_address}: {e}")
         return None
    except Exception as e:
        logger.error(f"An unexpected error occurred querying AbuseIPDB for {ip_address}: {e}", exc_info=True)
        return None
