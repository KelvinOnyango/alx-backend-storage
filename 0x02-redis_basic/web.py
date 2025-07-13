#!/usr/bin/env python3
"""
Web cache and tracker
"""

import requests
import redis
from functools import wraps

redis_client = redis.Redis()

def count_access(method):
    """Count URL accesses"""
    @wraps(method)
    def wrapper(url):
        redis_client.incr(f"count:{url}")
        return method(url)
    return wrapper

def cache_page(method):
    """Cache page with 10 second expiry"""
    @wraps(method)
    def wrapper(url):
        cached = redis_client.get(f"cache:{url}")
        if cached:
            return cached.decode('utf-8')
        html = method(url)
        redis_client.setex(f"cache:{url}", 10, html)
        return html
    return wrapper

@count_access
@cache_page
def get_page(url):
    """Get HTML content of URL"""
    return requests.get(url).text