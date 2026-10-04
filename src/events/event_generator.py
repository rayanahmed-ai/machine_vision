from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.models.vision_event import VisionEvent


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_event(
    *,
    event_type: str,
    camera: str | None,
    track_id: str | None,
    zone: str | None = None,
    identity: str | None = None,
    identity_status: str | None = None,
    identity_confidence: float | None = None,
    confidence: float = 0.0,
    metadata: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> VisionEvent:
    """Create a structured VisionEvent from CV state."""
    return VisionEvent(
        event_type=event_type,
        timestamp=timestamp or _utc_timestamp(),
        camera=camera,
        track_id=track_id,
        zone=zone,
        identity=identity,
        identity_status=identity_status,
        identity_confidence=identity_confidence,
        confidence=confidence,
        metadata=metadata or {},
    )
