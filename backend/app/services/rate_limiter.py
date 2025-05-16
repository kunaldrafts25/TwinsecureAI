import time
from typing import Dict, Optional
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = {}

    async def check_rate_limit(self, key: str) -> bool:
        """
        Check if a request should be rate limited.
        
        Args:
            key: Unique identifier for the rate limit (e.g., 'send_alert', 'send_report')
            
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)

        # Initialize or clean up old requests
        if key not in self.requests:
            self.requests[key] = []
        self.requests[key] = [t for t in self.requests[key] if t > window_start]

        # Check if we're over the limit
        if len(self.requests[key]) >= self.max_requests:
            return False

        # Add current request
        self.requests[key].append(now)
        return True

    def get_remaining_requests(self, key: str) -> int:
        """
        Get the number of remaining requests in the current time window.
        
        Args:
            key: Unique identifier for the rate limit
            
        Returns:
            int: Number of remaining requests
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)

        if key not in self.requests:
            return self.max_requests

        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        return max(0, self.max_requests - len(self.requests[key]))

    def get_reset_time(self, key: str) -> Optional[datetime]:
        """
        Get the time when the rate limit will reset.
        
        Args:
            key: Unique identifier for the rate limit
            
        Returns:
            Optional[datetime]: Time when rate limit resets, or None if no requests
        """
        if key not in self.requests or not self.requests[key]:
            return None

        oldest_request = min(self.requests[key])
        return oldest_request + timedelta(seconds=self.time_window)

    def reset(self, key: Optional[str] = None):
        """
        Reset rate limit for a specific key or all keys.
        
        Args:
            key: Optional key to reset. If None, resets all keys.
        """
        if key:
            self.requests[key] = []
        else:
            self.requests.clear() 