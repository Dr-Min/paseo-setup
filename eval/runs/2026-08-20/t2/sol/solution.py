import math
import threading
import time


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        """capacity: 버킷 최대 토큰 수. refill_rate: 초당 충전되는 토큰 수."""
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if not isinstance(refill_rate, (int, float)) or isinstance(refill_rate, bool):
            raise TypeError("refill_rate must be a number")
        if not math.isfinite(refill_rate) or refill_rate < 0:
            raise ValueError("refill_rate must be a finite non-negative number")

        self._capacity = capacity
        self._refill_rate = float(refill_rate)
        self._tokens = float(capacity)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def try_acquire(self, tokens: int = 1) -> bool:
        """토큰을 요청한다. 충분하면 차감하고 True, 부족하면 아무것도 하지 않고 False."""
        if not isinstance(tokens, int) or isinstance(tokens, bool) or tokens <= 0:
            raise ValueError("tokens must be a positive integer")

        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            if elapsed > 0:
                self._tokens = min(
                    float(self._capacity),
                    self._tokens + elapsed * self._refill_rate,
                )
                self._last_refill = now

            if self._tokens < tokens:
                return False

            self._tokens -= tokens
            return True
