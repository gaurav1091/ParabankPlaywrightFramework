import functools
import time
from typing import Any, Callable, TypeVar, cast

WrappedFunction = TypeVar("WrappedFunction", bound=Callable[..., Any])


def retry(max_retries: int = 1, delay: int = 1) -> Callable[[WrappedFunction], WrappedFunction]:
    def decorator(func: WrappedFunction) -> WrappedFunction:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc

                    if attempt < max_retries:
                        time.sleep(delay)
                        continue

                    raise last_exception from exc

            raise RuntimeError("Retry decorator exited unexpectedly without returning or raising.")

        return cast(WrappedFunction, wrapper)

    return decorator
