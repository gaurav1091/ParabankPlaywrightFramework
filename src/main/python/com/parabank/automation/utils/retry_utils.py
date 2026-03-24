import functools
import time
from typing import Callable


def retry(max_retries: int = 1, delay: int = 1):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay)
                    else:
                        raise last_exception

        return wrapper

    return decorator