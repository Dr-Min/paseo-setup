import threading
import time


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")

        self.capacity = capacity
        self.refill_rate = refill_rate
        self._tokens = float(capacity)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def try_acquire(self, tokens: int = 1) -> bool:
        if tokens < 0:
            raise ValueError("tokens must be non-negative")

        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            if elapsed > 0:
                self._tokens = min(
                    float(self.capacity),
                    self._tokens + elapsed * self.refill_rate,
                )
                self._last_refill = now

            if self._tokens < tokens:
                return False

            self._tokens -= tokens
            return True
