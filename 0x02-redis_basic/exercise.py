#!/usr/bin/env python3

"""
Cache module for Redis operations.
"""

import redis
import uuid
from typing import Union

class Cache:
    """
    Cache class for storing data in Redis.
    """

    def __Init__(self) -> None:
        """
        Initialize cache instance with Redis client and flush database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stores data in Redis with a random key
        Returns
        Args:
            data: The  data to store (can be str, bytes, int or float)
        Returns:
            str: The random key used to store the data
        """
        key = str(uuid.uuid4)
        self._redis.set(key, data)
        return key