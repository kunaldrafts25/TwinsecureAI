"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Response caching middleware for improved performance.
"""

import hashlib
import json
import time
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import logger, settings


class ResponseCache:
    """
    Simple in-memory cache for API responses with TTL-based expiration.
    
    For production with multiple workers, consider Redis instead.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of items in the cache
            default_ttl: Default time-to-live in seconds
        """
        self.cache: dict[str, dict] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> dict | None:
        """Get an item from the cache."""
        if key not in self.cache:
            self.misses += 1
            return None
        
        item = self.cache[key]
        
        # Check expiration
        if item["expires_at"] < time.time():
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return item["data"]
    
    def set(self, key: str, value: dict, ttl: int | None = None) -> None:
        """Set an item in the cache."""
        # Evict oldest item if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]["expires_at"]
            )
            del self.cache[oldest_key]
        
        # Store with expiration
        self.cache[key] = {
            "data": value,
            "expires_at": time.time() + (ttl or self.default_ttl),
        }
    
    def delete(self, key: str) -> None:
        """Delete an item from the cache."""
        self.cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear the entire cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> dict[str, int | float]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }


# Create global cache instance
# Note: Get settings safely with defaults
response_cache = ResponseCache(
    max_size=getattr(settings, "CACHE_MAX_SIZE", 1000),
    default_ttl=getattr(settings, "CACHE_DEFAULT_TTL", 60)
)


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware for caching API responses.
    
    Caches GET/HEAD requests to improve performance for frequently accessed endpoints.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        cache_instance: ResponseCache = response_cache,
        cacheable_paths: list[str] | None = None,
        cacheable_methods: set[str] | None = None,
        exclude_paths: list[str] | None = None,
        exclude_query_params: list[str] | None = None,
        vary_headers: list[str] | None = None,
    ):
        """
        Initialize the cache middleware.
        
        Args:
            app: The ASGI application
            cache_instance: The cache instance to use
            cacheable_paths: List of path prefixes that can be cached
            cacheable_methods: Set of HTTP methods that can be cached
            exclude_paths: List of path prefixes to never cache
            exclude_query_params: Query parameters to exclude from cache key
            vary_headers: Headers to include in cache key
        """
        super().__init__(app)
        self.cache = cache_instance
        self.cacheable_paths = cacheable_paths or ["/api/v1/"]
        self.cacheable_methods = cacheable_methods or {"GET", "HEAD"}
        self.exclude_paths = exclude_paths or [
            "/api/v1/auth/",
            "/api/v1/users/me",
            "/api/v1/health",
            "/metrics",
        ]
        self.exclude_query_params = exclude_query_params or ["_", "timestamp"]
        self.vary_headers = vary_headers or ["Accept", "Accept-Encoding"]
    
    def is_cacheable(self, request: Request) -> bool:
        """Check if a request is cacheable."""
        # Check HTTP method
        if request.method not in self.cacheable_methods:
            return False
        
        path = request.url.path
        
        # Check exclude list first
        if any(path.startswith(exclude) for exclude in self.exclude_paths):
            return False
        
        # Check cacheable list
        return any(path.startswith(cacheable) for cacheable in self.cacheable_paths)
    
    def get_cache_key(self, request: Request) -> str:
        """Generate a cache key for a request."""
        path = request.url.path
        query_params = {
            k: v for k, v in request.query_params.items()
            if k not in self.exclude_query_params
        }
        
        # Get relevant headers
        headers = {
            header.lower(): request.headers[header.lower()]
            for header in self.vary_headers
            if header.lower() in request.headers
        }
        
        # Create cache key
        key_dict = {
            "path": path,
            "query_params": query_params,
            "headers": headers,
        }
        
        key_json = json.dumps(key_dict, sort_keys=True)
        return hashlib.md5(key_json.encode()).hexdigest()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and cache the response if applicable."""
        # Check if cacheable
        if not self.is_cacheable(request):
            return await call_next(request)
        
        # Generate cache key
        cache_key = self.get_cache_key(request)
        
        # Check cache
        cached_response = self.cache.get(cache_key)
        if cached_response:
            response = Response(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers=cached_response["headers"],
                media_type=cached_response["media_type"],
            )
            response.headers["X-Cache"] = "HIT"
            return response
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if 200 <= response.status_code < 400:
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Create new response
            new_response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
            
            # Cache it
            self.cache.set(
                cache_key,
                {
                    "content": response_body,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type,
                },
            )
            
            new_response.headers["X-Cache"] = "MISS"
            return new_response
        
        return response


def add_cache_middleware(app: FastAPI) -> None:
    """Add cache middleware to the FastAPI application."""
    app.add_middleware(CacheMiddleware)
