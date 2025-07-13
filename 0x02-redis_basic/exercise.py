#!/usr/bin/env python3
"""
Cache module for Redis operations with call tracking and history.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count how many times a method is called.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that increments the call count.
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that stores inputs and outputs in Redis lists.
        """
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        
        # Store input arguments
        self._redis.rpush(input_key, str(args))
        
        # Execute the wrapped function to get the output
        output = method(self, *args, **kwargs)
        
        # Store the output
        self._redis.rpush(output_key, output)
        
        return output
    return wrapper


class Cache:
    """
    Cache class for storing data in Redis with call tracking.
    """

    def __init__(self) -> None:
        """
        Initialize the Cache with a Redis client and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random key and return the key.
        
        Args:
            data: Data to store (str, bytes, int, or float)
            
        Returns:
            str: The generated key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
        self, 
        key: str, 
        fn: Optional[Callable] = None
    ) -> Union[str, bytes, int, float]:
        """
        Retrieve data from Redis and optionally apply a conversion function.
        
        Args:
            key: The key to retrieve
            fn: Optional conversion function
            
        Returns:
            The retrieved data, optionally converted
        """
        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """
        Get a string from Redis.
        
        Args:
            key: The key to retrieve
            
        Returns:
            str: The decoded string
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """
        Get an integer from Redis.
        
        Args:
            key: The key to retrieve
            
        Returns:
            int: The converted integer
        """
        return self.get(key, fn=int)


def replay(method: Callable) -> None:
    """
    Display the history of calls of a particular function.
    
    Args:
        method: The method to replay history for
    """
    qualname = method.__qualname__
    redis_instance = method.__self__._redis
    
    count = redis_instance.get(qualname)
    count = int(count) if count else 0
    
    inputs = redis_instance.lrange(f"{qualname}:inputs", 0, -1)
    outputs = redis_instance.lrange(f"{qualname}:outputs", 0, -1)
    
    print(f"{qualname} was called {count} times:")
    for args, output in zip(inputs, outputs):
        print(f"{qualname}(*{args.decode('utf-8')}) -> {output.decode('utf-8')}")