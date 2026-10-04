from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class VisionEvent(BaseModel):
    """Structured output event published downstream."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    timestamp: str
    camera: str | None = None
    track_id: str | None = None
    zone: str | None = None
    identity: str | None = None
    identity_status: str | None = None
    identity_confidence: float | None = None
    confidence: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)
