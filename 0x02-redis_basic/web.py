import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis client
redis_client = redis.Redis()

def track_access(method: Callable) -> Callable:
    """Decorator to track URL access counts."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function that tracks URL access counts."""
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return method(url)
    return wrapper

def cache_page(expiration: int = 10) -> Callable:
    """Decorator to cache page content with expiration."""
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(url: str) -> str:
            """Wrapper function that caches page content."""
            cache_key = f"cache:{url}"
            # Try to get cached content
            cached_content = redis_client.get(cache_key)
            if cached_content:
                return cached_content.decode('utf-8')
            
            # If not cached, fetch and store
            content = method(url)
            redis_client.setex(cache_key, expiration, content)
            return content
        return wrapper
    return decorator

@track_access
@cache_page(expiration=10)
def get_page(url: str) -> str:
    """Fetch the HTML content of a URL with caching and access tracking."""
    response = requests.get(url)
    return response.text