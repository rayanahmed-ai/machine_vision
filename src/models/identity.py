from __future__ import annotations

from enum import Enum


class IdentityStatus(str, Enum):
    """Resolution status for a detected person."""

    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    AMBIGUOUS = "AMBIGUOUS"
