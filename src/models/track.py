from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .identity import IdentityStatus


class Track(BaseModel):
    """Persistent state for an observed person track."""

    track_id: str
    camera: str | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    position: tuple[float, float] | None = None
    previous_position: tuple[float, float] | None = None
    zone: str | None = None
    previous_zone: str | None = None
    entered_zone_at: datetime | None = None
    identity: str | None = None
    identity_status: IdentityStatus = IdentityStatus.UNKNOWN
    identity_confidence: float = 0.0
    position_history: list[tuple[float, float]] = Field(default_factory=list)
    last_loiter_event_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)
