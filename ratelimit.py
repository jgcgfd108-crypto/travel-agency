"""Tiny in-memory sliding-window limiter (per process; see README for multi-worker notes)."""
import threading
import time


class RateLimiter:
    def __init__(self, limit, window):
        self.limit, self.window = limit, window
        self._hits, self._lock = {}, threading.Lock()

    def allow(self, key):
        now = time.time()
        with self._lock:
            hits = [t for t in self._hits.get(key, []) if now - t < self.window]
            if len(hits) >= self.limit:
                self._hits[key] = hits
                return False
            hits.append(now)
            self._hits[key] = hits
            if len(self._hits) > 5000:     # keep memory bounded
                self._hits = {k: v for k, v in self._hits.items() if v and now - v[-1] < self.window}
            return True
