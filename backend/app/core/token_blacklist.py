"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Token blacklist management for JWT token revocation.
"""

import hashlib
from datetime import datetime, timedelta, timezone

from app.core.config import logger, settings

# In-memory blacklist (fallback if Redis not available)
_in_memory_blacklist: dict[str, datetime] = {}


def _get_token_hash(token: str) -> str:
    """Generate a SHA256 hash of the token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


async def add_to_blacklist(token: str, expires_at: datetime | None = None) -> bool:
    """
    Add a token to the blacklist.
    
    Args:
        token: The JWT token to blacklist
        expires_at: When the token expires (if None, uses default expiry)
    
    Returns:
        True if successfully added, False otherwise
    """
    if not settings.security.JWT_BLACKLIST_ENABLED:
        logger.debug("JWT blacklist is disabled")
        return False
    
    try:
        token_hash = _get_token_hash(token)
        
        # If expires_at not provided, use default token expiry
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        # Try Redis first if available
        if settings.cache.REDIS_URL:
            try:
                import redis.asyncio as redis
                
                password = None
                if settings.cache.REDIS_PASSWORD:
                    password = settings.cache.REDIS_PASSWORD.get_secret_value()
                
                redis_client = redis.from_url(
                    settings.cache.REDIS_URL,
                    password=password,
                    decode_responses=True
                )
                
                # Calculate TTL
                ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())
                
                if ttl > 0:
                    await redis_client.setex(
                        f"blacklist:{token_hash}",
                        ttl,
                        "1"
                    )
                    await redis_client.close()
                    logger.info(f"Token blacklisted in Redis (expires in {ttl}s)")
                    return True
                
            except ImportError:
                logger.warning("Redis not available, falling back to in-memory blacklist")
            except Exception as e:
                logger.error(f"Error adding token to Redis blacklist: {e}")
        
        # Fallback to in-memory blacklist
        _in_memory_blacklist[token_hash] = expires_at
        logger.info(f"Token blacklisted in memory (expires at {expires_at})")
        return True
        
    except Exception as e:
        logger.error(f"Error adding token to blacklist: {e}")
        return False


async def is_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted.
    
    Args:
        token: The JWT token to check
    
    Returns:
        True if token is blacklisted, False otherwise
    """
    if not settings.security.JWT_BLACKLIST_ENABLED:
        return False
    
    try:
        token_hash = _get_token_hash(token)
        
        # Try Redis first if available
        if settings.cache.REDIS_URL:
            try:
                import redis.asyncio as redis
                
                password = None
                if settings.cache.REDIS_PASSWORD:
                    password = settings.cache.REDIS_PASSWORD.get_secret_value()
                
                redis_client = redis.from_url(
                    settings.cache.REDIS_URL,
                    password=password,
                    decode_responses=True
                )
                
                result = await redis_client.get(f"blacklist:{token_hash}")
                await redis_client.close()
                
                if result:
                    logger.debug("Token found in Redis blacklist")
                    return True
                    
            except ImportError:
                pass
            except Exception as e:
                logger.error(f"Error checking Redis blacklist: {e}")
        
        # Check in-memory blacklist
        if token_hash in _in_memory_blacklist:
            expires_at = _in_memory_blacklist[token_hash]
            
            # Remove expired entries
            if datetime.now(timezone.utc) > expires_at:
                del _in_memory_blacklist[token_hash]
                return False
            
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking token blacklist: {e}")
        return False


def cleanup_expired_tokens() -> None:
    """Clean up expired tokens from in-memory blacklist."""
    now = datetime.now(timezone.utc)
    expired = [
        token_hash
        for token_hash, expires_at in _in_memory_blacklist.items()
        if now > expires_at
    ]
    
    for token_hash in expired:
        del _in_memory_blacklist[token_hash]
    
    if expired:
        logger.debug(f"Cleaned up {len(expired)} expired tokens from blacklist")









