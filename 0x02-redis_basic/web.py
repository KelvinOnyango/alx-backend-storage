#!/usr/bin/env python3
"""
Web cache and tracker implementation with Redis.
"""

import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis client connection
redis_client = redis.Redis()


def count_access(method: Callable) -> Callable:
    """
    Decorator to count how many times a URL has been accessed.
    Increments the count each time the URL is requested.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function that tracks URL access counts."""
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return method(url)
    return wrapper


def cache_result(expiration: int = 10) -> Callable:
    """
    Decorator to cache the result of a function with expiration.
    Args:
        expiration: Time in seconds until the cache expires (default: 10)
    """
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(url: str) -> str:
            """Wrapper function that implements caching logic."""
            cache_key = f"cache:{url}"
            
            # Check if result is cached
            cached_content = redis_client.get(cache_key)
            if cached_content:
                return cached_content.decode('utf-8')
            
            # If not cached, fetch and store
            content = method(url)
            redis_client.setex(cache_key, expiration, content)
            return content
        return wrapper
    return decorator


@count_access
@cache_result(expiration=10)
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL with caching and access tracking.
    Args:
        url: The URL to fetch content from
    Returns:
        The HTML content as a string
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        # Return empty string on error to match expected behavior
        return ""