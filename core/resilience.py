"""
Resilience Manager for handling API flakiness and rate limits.
"""

import asyncio
import functools
import logging
import time
from typing import Callable, Any, Type, Union, Tuple

logger = logging.getLogger(__name__)

class CircuitBreakerOpenError(Exception):
    """Raised when the circuit breaker is open."""
    pass

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception
):
    """
    Exponential backoff retry decorator.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"Postignut maksimalni broj pokušaja ({max_attempts}) za {func.__name__}: {e}")
                        raise e
                    
                    logger.warning(f"Pokušaj {attempt} nije uspeo za {func.__name__}. Ponovni pokušaj za {current_delay}s... (Greška: {e})")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Circuit Breaker pattern implementation.
    """
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

    def __call__(self, func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    logger.info("Circuit Breaker: Prelazak u HALF_OPEN stanje.")
                    self.state = "HALF_OPEN"
                else:
                    raise CircuitBreakerOpenError(f"Circuit Breaker je otvoren za {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    logger.info("Circuit Breaker: Uspešan poziv! Vraćanje u CLOSED stanje.")
                    self.reset()
                return result
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    logger.error(f"Circuit Breaker: Prag grešaka dostignut ({self.failure_count}). Otvaranje kola.")
                    self.state = "OPEN"
                
                raise e
        return wrapper

    def reset(self):
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = 0
