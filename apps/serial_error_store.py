"""In-memory, thread-safe error store for the serial daemon."""
from collections import deque
from threading import Lock

from apps.serial_error import SerialError


class ErrorStore:
    """Thread-safe ring buffer for error dicts using deque(maxlen=20)."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._buf: deque[SerialError] = deque(maxlen=20)

    def record(self, error: SerialError) -> None:
        """Record a new error entry."""
        with self._lock:
            self._buf.append(error)

    def get_last(self) -> SerialError | None:
        """Return the most recent error or None if empty."""
        with self._lock:
            if not self._buf:
                return None
            return self._buf[-1]

    def get_recent(self, limit: int = 20) -> list[SerialError]:
        """Return up to `limit` most recent errors, newest first."""
        with self._lock:
            if limit <= 0:
                return []
            items = list(self._buf)
            return items[-limit:][::-1]
