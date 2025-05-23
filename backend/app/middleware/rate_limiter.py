"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

"""
Rate limiter middleware for FastAPI.
This middleware uses the RateLimiter service to limit requests based on client IP.
"""

import re
import time
from typing import Any, Callable, Dict, List, Optional

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import logger, settings
from app.services.rate_limiter import RateLimiter


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests based on client IP.

    Attributes:
        rate_limiter: The rate limiter service
        exclude_paths: List of path patterns to exclude from rate limiting
        get_identifier: Function to get the identifier for rate limiting (default: client IP)
    """

    def __init__(
        self,
        app: ASGIApp,
        max_requests: int = 100,
        time_window: int = 60,
        exclude_paths: Optional[List[str]] = None,
        get_identifier: Optional[Callable[[Request], str]] = None,
    ):
        """
        Initialize the rate limiter middleware.

        Args:
            app: The ASGI application
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
            exclude_paths: List of path patterns to exclude from rate limiting
            get_identifier: Function to get the identifier for rate limiting
        """
        super().__init__(app)
        self.rate_limiter = RateLimiter(
            max_requests=max_requests, time_window=time_window
        )
        self.exclude_paths = exclude_paths or []
        self.get_identifier = get_identifier or self._default_identifier

        # Compile regex patterns for excluded paths
        self.exclude_patterns = [re.compile(pattern) for pattern in self.exclude_paths]

        logger.info(
            f"Rate limiter middleware initialized with {max_requests} requests per {time_window} seconds"
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request through the rate limiter.

        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler

        Returns:
            Response: The response from the next handler or a 429 Too Many Requests response
        """
        # Skip rate limiting for excluded paths
        path = request.url.path
        if any(pattern.match(path) for pattern in self.exclude_patterns):
            return await call_next(request)

        # Get identifier for rate limiting
        identifier = self.get_identifier(request)

        # Check rate limit
        allowed = await self.rate_limiter.check_rate_limit(identifier)

        # Get remaining requests for headers
        remaining = self.rate_limiter.get_remaining_requests(identifier)

        if not allowed:
            # Rate limit exceeded
            logger.warning(f"Rate limit exceeded for {identifier} on {path}")

            # Create response with rate limit headers
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

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response

    def _default_identifier(self, request: Request) -> str:
        """
        Get the default identifier for rate limiting (client IP).

        Args:
            request: The incoming request

        Returns:
            str: The client IP address
        """
        # Try to get the real IP from X-Forwarded-For header
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get the first IP in the list (client IP)
            return forwarded_for.split(",")[0].strip()

        # Fall back to the client host
        return request.client.host if request.client else "unknown"
