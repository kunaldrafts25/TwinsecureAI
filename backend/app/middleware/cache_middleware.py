"""
Caching middleware for TwinSecure backend.

This module provides middleware for caching responses to improve performance.
"""

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable, Dict, List, Optional, Set, Union
import hashlib
import json
import time
from datetime import datetime, timedelta

from app.core.config import settings, logger

class ResponseCache:
    """
    Simple in-memory cache for API responses.
    
    This class provides a simple in-memory cache for API responses
    with TTL-based expiration.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of items in the cache
            default_ttl: Default time-to-live in seconds
        """
        self.cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Dict]:
        """
        Get an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Optional[Dict]: The cached item or None if not found or expired
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        item = self.cache[key]
        
        # Check if the item has expired
        if item["expires_at"] < time.time():
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return item["data"]
    
    def set(self, key: str, value: Dict, ttl: Optional[int] = None) -> None:
        """
        Set an item in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional)
        """
        # If the cache is full, remove the oldest item
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["expires_at"])
            del self.cache[oldest_key]
        
        # Set the item with expiration time
        self.cache[key] = {
            "data": value,
            "expires_at": time.time() + (ttl or self.default_ttl)
        }
    
    def delete(self, key: str) -> None:
        """
        Delete an item from the cache.
        
        Args:
            key: Cache key
        """
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """
        Clear the entire cache.
        """
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Union[int, float]]:
        """
        Get cache statistics.
        
        Returns:
            Dict[str, Union[int, float]]: Cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }

# Create a global cache instance
response_cache = ResponseCache(
    max_size=settings.CACHE_MAX_SIZE,
    default_ttl=settings.CACHE_DEFAULT_TTL
)

class CacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware for caching API responses.
    
    This middleware caches API responses to improve performance
    for frequently accessed endpoints.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        cache_instance: ResponseCache = response_cache,
        cacheable_paths: Optional[List[str]] = None,
        cacheable_methods: Optional[Set[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        exclude_query_params: Optional[List[str]] = None,
        vary_headers: Optional[List[str]] = None,
    ):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
            cache_instance: The cache instance to use
            cacheable_paths: List of path prefixes that can be cached
            cacheable_methods: Set of HTTP methods that can be cached
            exclude_paths: List of path prefixes that should not be cached
            exclude_query_params: List of query parameters to exclude from cache key
            vary_headers: List of headers to include in the cache key
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
        """
        Check if a request is cacheable.
        
        Args:
            request: The HTTP request
            
        Returns:
            bool: True if the request is cacheable, False otherwise
        """
        # Check HTTP method
        if request.method not in self.cacheable_methods:
            return False
        
        # Check path
        path = request.url.path
        
        # Check if path is in exclude list
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return False
        
        # Check if path is in cacheable list
        for cacheable_path in self.cacheable_paths:
            if path.startswith(cacheable_path):
                return True
        
        return False
    
    def get_cache_key(self, request: Request) -> str:
        """
        Generate a cache key for a request.
        
        Args:
            request: The HTTP request
            
        Returns:
            str: The cache key
        """
        # Get path and query parameters
        path = request.url.path
        query_params = dict(request.query_params)
        
        # Remove excluded query parameters
        for param in self.exclude_query_params:
            if param in query_params:
                del query_params[param]
        
        # Get relevant headers
        headers = {}
        for header in self.vary_headers:
            if header.lower() in request.headers:
                headers[header.lower()] = request.headers[header.lower()]
        
        # Create a dictionary with all components
        key_dict = {
            "path": path,
            "query_params": query_params,
            "headers": headers,
        }
        
        # Convert to JSON and hash
        key_json = json.dumps(key_dict, sort_keys=True)
        return hashlib.md5(key_json.encode()).hexdigest()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and cache the response if applicable.
        
        Args:
            request: The HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            Response: The HTTP response
        """
        # Check if the request is cacheable
        if not self.is_cacheable(request):
            return await call_next(request)
        
        # Generate cache key
        cache_key = self.get_cache_key(request)
        
        # Check if the response is in the cache
        cached_response = self.cache.get(cache_key)
        if cached_response:
            # Return cached response
            response = Response(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers=cached_response["headers"],
                media_type=cached_response["media_type"]
            )
            response.headers["X-Cache"] = "HIT"
            return response
        
        # Process the request through the next handler
        response = await call_next(request)
        
        # Cache the response if it's successful
        if 200 <= response.status_code < 400:
            # Get response content
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Create a new response with the same content
            new_response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            # Cache the response
            self.cache.set(
                cache_key,
                {
                    "content": response_body,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type
                }
            )
            
            new_response.headers["X-Cache"] = "MISS"
            return new_response
        
        return response

def add_cache_middleware(app: FastAPI) -> None:
    """
    Add cache middleware to the FastAPI application.
    
    Args:
        app: The FastAPI application
    """
    # Add cache middleware
    app.add_middleware(CacheMiddleware)
