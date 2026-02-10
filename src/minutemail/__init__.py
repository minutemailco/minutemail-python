"""MinuteMail Python SDK - Official client for the MinuteMail API."""

__version__ = "1.0.0"

from .client import MinuteMailClient
from .errors import APIError, MinuteMailError, TransportError

__all__ = ["MinuteMailClient", "APIError", "MinuteMailError", "TransportError"]
