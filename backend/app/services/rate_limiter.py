"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Rate limiting service with Redis sliding window support.
"""

import time
from datetime import datetime, timedelta

from app.core.config import logger, settings


class RateLimiter:
    """
    Rate limiter with Redis backend support and in-memory fallback.
    Uses sliding window algorithm for accurate rate limiting.
    """
    
    def __init__(self, max_requests: int, time_window: int):
        """
        Initialize rate limiter with Redis support if available.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: dict[str, list[datetime]] = {}
        self.redis_client = None
        
        # Try to initialize Redis client if available
        if hasattr(settings, "REDIS_URL") and settings.REDIS_URL:
            try:
                import redis.asyncio as redis
                
                self.redis_client = redis.from_url(settings.REDIS_URL)
                logger.info("Rate limiter using Redis backend")
            
            except ImportError:
                logger.warning("redis not installed. Using in-memory rate limiting.")
            
            except Exception as e:
                logger.warning(
                    f"Failed to connect to Redis for rate limiting: {e}. "
                    "Using in-memory."
                )
    
    async def check_rate_limit(self, key: str) -> bool:
        """
        Check if a request should be rate limited.
        Uses Redis if available, otherwise falls back to in-memory storage.
        
        Args:
            key: Unique identifier for the rate limit (e.g., IP address, user ID)
            
        Returns:
            True if request is allowed, False if rate limited
        """
        if self.redis_client:
            return await self._check_rate_limit_redis(key)
        else:
            return await self._check_rate_limit_memory(key)
    
    async def _check_rate_limit_redis(self, key: str) -> bool:
        """
        Check rate limit using Redis sorted set (sliding window algorithm).
        
        Args:
            key: Unique identifier
            
        Returns:
            True if allowed, False if rate limited
        """
        try:
            redis_key = f"rate_limit:{key}"
            now = int(time.time())
            window_start = now - self.time_window
            
            # Use Redis sorted set to track requests
            pipe = self.redis_client.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(redis_key, 0, window_start)
            
            # Count current entries in the window
            pipe.zcard(redis_key)
            
            # Add current request
            pipe.zadd(redis_key, {str(now): now})
            
            # Set expiry to clean up old keys
            pipe.expire(redis_key, self.time_window + 10)
            
            results = await pipe.execute()
            current_count = results[1]  # Count before adding new request
            
            if current_count >= self.max_requests:
                logger.debug(
                    f"Rate limit exceeded for {key}: "
                    f"{current_count}/{self.max_requests} in {self.time_window}s window"
                )
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}, falling back to memory")
            return await self._check_rate_limit_memory(key)
    
    async def _check_rate_limit_memory(self, key: str) -> bool:
        """
        Check rate limit using in-memory storage (sliding window).
        
        Args:
            key: Unique identifier
            
        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)
        
        # Initialize or clean up old requests
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove requests outside the sliding window
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        
        # Check if we're over the limit
        if len(self.requests[key]) >= self.max_requests:
            logger.debug(
                f"Rate limit exceeded for {key}: "
                f"{len(self.requests[key])}/{self.max_requests} "
                f"in {self.time_window}s window"
            )
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True
    
    async def get_remaining_requests(self, key: str) -> int:
        """
        Get the number of remaining requests in the current time window.
        
        Args:
            key: Unique identifier for the rate limit
            
        Returns:
            Number of remaining requests
        """
        if self.redis_client:
            try:
                redis_key = f"rate_limit:{key}"
                now = int(time.time())
                window_start = now - self.time_window
                
                # Count requests in current window
                count = await self.redis_client.zcount(redis_key, window_start, now)
                return max(0, self.max_requests - count)
            
            except Exception as e:
                logger.error(f"Failed to get remaining requests from Redis: {e}")
                return self.max_requests  # Assume unlimited on error
        
        # In-memory fallback
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)
        
        if key not in self.requests:
            return self.max_requests
        
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        return max(0, self.max_requests - len(self.requests[key]))
    
    def get_reset_time(self, key: str) -> datetime | None:
        """
        Get the time when the rate limit will reset.
        
        Args:
            key: Unique identifier for the rate limit
            
        Returns:
            Time when rate limit resets, or None if no requests
        """
        if key not in self.requests or not self.requests[key]:
            return None
        
        oldest_request = min(self.requests[key])
        return oldest_request + timedelta(seconds=self.time_window)
    
    async def reset(self, key: str | None = None):
        """
        Reset rate limit for a specific key or all keys.
        
        Args:
            key: Optional key to reset. If None, resets all keys.
        """
        if self.redis_client:
            try:
                if key:
                    redis_key = f"rate_limit:{key}"
                    await self.redis_client.delete(redis_key)
                else:
                    # Delete all rate limit keys
                    pattern = "rate_limit:*"
                    async for key in self.redis_client.scan_iter(pattern):
                        await self.redis_client.delete(key)
                
                logger.info(f"Rate limit reset for: {key or 'all keys'}")
            
            except Exception as e:
                logger.error(f"Failed to reset rate limit in Redis: {e}")
        
        # Also reset in-memory
        if key:
            self.requests[key] = []
        else:
            self.requests.clear()
    
    async def close(self):
        """Close Redis connection (call on app shutdown)."""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Rate limiter Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
