"""
Rate Limiting Utility

Centralized rate limiting for API calls to prevent hitting rate limits.
"""

import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Centralized rate limiter for managing API request rates.
    """
    
    def __init__(self):
        self.last_request_times: Dict[str, float] = {}
        self.rate_limits = {
            'serpapi': 1.0,  # 1 second between SerpAPI requests
            'gemini': 0.5,   # 0.5 seconds between Gemini requests  
            'google_ads': 0.1,  # 0.1 seconds between Google Ads requests
            'browser_scraping': 2.0  # 2 seconds between web scraping requests
        }
    
    def wait_if_needed(self, service: str) -> None:
        """
        Wait if necessary to maintain rate limits for the specified service.
        
        Args:
            service: The service name (e.g., 'serpapi', 'gemini', etc.)
        """
        if service not in self.rate_limits:
            logger.warning(f"Unknown service '{service}' for rate limiting")
            return
        
        current_time = time.time()
        last_request_time = self.last_request_times.get(service, 0)
        min_interval = self.rate_limits[service]
        
        time_since_last_request = current_time - last_request_time
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            logger.info(f"Rate limiting {service}: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_times[service] = time.time()
    
    def set_rate_limit(self, service: str, interval: float) -> None:
        """
        Set or update the rate limit for a service.
        
        Args:
            service: The service name
            interval: Minimum interval between requests in seconds
        """
        self.rate_limits[service] = interval
        logger.info(f"Rate limit for {service} set to {interval} seconds")

# Global rate limiter instance
rate_limiter = RateLimiter()
