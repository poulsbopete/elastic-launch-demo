"""Thread-safe shared context store for log-trace correlation.

The trace generator writes (trace_id, span_id) per service after each trace batch.
Service log emitters read the latest context to correlate their logs with active traces.
Entries expire after a configurable TTL so stale correlations don't persist.
"""

from __future__ import annotations

import threading
import time


class TraceContextStore:
    """Maps service_name -> (trace_id, span_id, timestamp) with TTL expiry."""

    def __init__(self, ttl_seconds: float = 5.0):
        self._store: dict[str, tuple[str, str, float]] = {}
        self._lock = threading.Lock()
        self._ttl = ttl_seconds

    def set(self, service_name: str, trace_id: str, span_id: str) -> None:
        with self._lock:
            self._store[service_name] = (trace_id, span_id, time.monotonic())

    def get(self, service_name: str) -> tuple[str | None, str | None]:
        with self._lock:
            entry = self._store.get(service_name)
            if entry is None:
                return None, None
            trace_id, span_id, ts = entry
            if time.monotonic() - ts > self._ttl:
                del self._store[service_name]
                return None, None
            return trace_id, span_id


# Module-level singleton — imported by trace_generator and base_service
_trace_context_store = TraceContextStore()
