from typing import Optional


class MinuteMailError(Exception):
    """Base error for the MinuteMail SDK."""


class TransportError(MinuteMailError):
    """Raised when an HTTP request cannot be completed."""


class APIError(MinuteMailError):
    """Raised for non-2xx API responses."""

    def __init__(
        self,
        status_code: int,
        error: Optional[str] = None,
        message: Optional[str] = None,
        response_text: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.error = error
        self.message = message
        self.response_text = response_text
        parts = [f"status={status_code}"]
        if error:
            parts.append(f"error={error}")
        if message:
            parts.append(f"message={message}")
        elif response_text and response_text.strip():
            # Only include response text when a structured message is missing.
            preview = response_text.strip()
            parts.append(f"response={preview[:200]}")
        super().__init__(", ".join(parts))
