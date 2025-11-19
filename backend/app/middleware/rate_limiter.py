"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Rate limiter middleware for FastAPI.
"""

import re
import time
from collections.abc import Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import logger
from app.services.rate_limiter import RateLimiter


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests based on client IP.
    
    Tracks requests per identifier (default: IP address) and returns 429
    when the limit is exceeded. Adds rate limit headers to all responses.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        max_requests: int = 100,
        time_window: int = 60,
        exclude_paths: list[str] | None = None,
        get_identifier: Callable[[Request], str] | None = None,
    ):
        """
        Initialize the rate limiter middleware.
        
        Args:
            app: The ASGI application
            max_requests: Maximum requests allowed in the time window
            time_window: Time window in seconds
            exclude_paths: List of regex path patterns to exclude
            get_identifier: Custom function to identify clients
        """
        super().__init__(app)
        self.rate_limiter = RateLimiter(
            max_requests=max_requests,
            time_window=time_window
        )
        
        self.exclude_paths = exclude_paths or []
        self.get_identifier = get_identifier or self._default_identifier
        
        # Compile regex patterns for excluded paths
        self.exclude_patterns = [re.compile(pattern) for pattern in self.exclude_paths]
        
        logger.info(
            f"Rate limiter initialized: {max_requests} requests per {time_window}s"
        )
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request through the rate limiter.
        
        Returns 429 if rate limit exceeded, otherwise passes to next handler.
        """
        # Skip rate limiting for excluded paths
        path = request.url.path
        if any(pattern.match(path) for pattern in self.exclude_patterns):
            return await call_next(request)
        
        # Get identifier for rate limiting
        identifier = self.get_identifier(request)
        
        # Check rate limit
        allowed = await self.rate_limiter.check_rate_limit(identifier)
        remaining = self.rate_limiter.get_remaining_requests(identifier)
        
        if not allowed:
            # Rate limit exceeded
            logger.warning(f"Rate limit exceeded for {identifier} on {path}")
            
            response = Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="text/plain",
            )
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(
                int(time.time() + self.rate_limiter.time_window)
            )
            
            return response
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _default_identifier(self, request: Request) -> str:
        """
        Get the client identifier for rate limiting (client IP).
        
        Handles X-Forwarded-For for proxied requests.
        """
        # Try to get the real IP from X-Forwarded-For header
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get the first IP in the list (client IP)
            return forwarded_for.split(",")[0].strip()
        
        # Fall back to the client host
        return request.client.host if request.client else "unknown"
