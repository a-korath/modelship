
from fastapi import Depends, HTTPException, status
import time

from src.api.middleware.auth import APIKey, validate_api_key

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        self.refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        refill_amount = elapsed * self.refill_rate
        if refill_amount > 0:
            self.tokens = min(self.capacity, self.tokens + refill_amount)
            self.last_refill = now

class RateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets: dict[str, TokenBucket] = {}

    def is_allowed(self, key: str) -> bool:
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(self.capacity, self.refill_rate)
        return self._buckets[key].consume()

rate_limiter = RateLimiter(capacity=60, refill_rate=1)  # 60 requests per minute

def rate_limit(api_key: APIKey = Depends(validate_api_key)):
    if not rate_limiter.is_allowed(api_key.key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
        )
