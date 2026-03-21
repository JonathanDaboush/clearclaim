"""Sliding-window rate limiter keyed on (client_ip, endpoint).

This is an in-process implementation that is sufficient for a single-process
server.  For a multi-process/multi-server deployment replace the in-memory
store with a shared Redis ZSET (the algorithm is identical).

Usage in main.py request handler:
    from utils.rate_limiter import RateLimiter, RateLimitExceeded

    try:
        _rate_limiter.check(client_ip, path)
    except RateLimitExceeded as exc:
        # return 429 response
        ...
"""
import threading
import time
from collections import deque
from typing import Dict, Deque, Tuple


class RateLimitExceeded(Exception):
    """Raised when a client exceeds the allowed request rate for an endpoint."""
    def __init__(self, endpoint: str, limit: int, window: int):
        self.endpoint = endpoint
        self.limit = limit
        self.window = window
        super().__init__(
            f"Rate limit exceeded for {endpoint!r}: "
            f"max {limit} requests per {window}s"
        )


import os

# Per-endpoint policies: (max_requests, window_seconds)
# These cover all sensitive surfaces identified in the security review.
_RATE_MULTIPLIER = 20 if os.environ.get("ENV") == "development" else 1
_ENDPOINT_POLICIES: Dict[str, Tuple[int, int]] = {
    "/user/login":                     (10 * _RATE_MULTIPLIER, 60),
    "/auth/authenticate_user":         (10 * _RATE_MULTIPLIER, 60),
    "/user/verify_totp":               (5  * _RATE_MULTIPLIER, 60),
    "/auth/verify_totp":               (5  * _RATE_MULTIPLIER, 60),
    "/signing/sign":                   (5  * _RATE_MULTIPLIER, 60),
    "/signing/verify_totp":            (5  * _RATE_MULTIPLIER, 60),
    "/user/initiate_password_reset":   (5  * _RATE_MULTIPLIER, 300),
    "/auth/initiate_password_reset":   (5  * _RATE_MULTIPLIER, 300),
    "/user/complete_password_reset":   (5  * _RATE_MULTIPLIER, 300),
    "/auth/complete_password_reset":   (5  * _RATE_MULTIPLIER, 300),
    "/user/signup":                    (5  * _RATE_MULTIPLIER, 300),
    "/auth/create_user":               (5  * _RATE_MULTIPLIER, 300),
}

# Default policy for all other POST endpoints (generous but present)
_DEFAULT_POLICY: Tuple[int, int] = (60, 60)


class RateLimiter:
    """Thread-safe sliding-window rate limiter."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # key: (ip, endpoint) → deque of request timestamps (float, monotonic)
        self._windows: Dict[Tuple[str, str], Deque[float]] = {}

    def check(self, client_ip: str, endpoint: str) -> None:
        """Record a request and raise RateLimitExceeded if the client is over limit.

        Only enforces for POST requests on the routes that match _ENDPOINT_POLICIES
        (or the default policy).  GET requests are not rate-limited here because
        they are read-only.
        """
        limit, window = _ENDPOINT_POLICIES.get(endpoint, _DEFAULT_POLICY)
        key = (client_ip, endpoint)
        now = time.monotonic()
        cutoff = now - window

        with self._lock:
            q = self._windows.setdefault(key, deque())
            # Evict timestamps outside the current window
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= limit:
                raise RateLimitExceeded(endpoint, limit, window)
            q.append(now)
