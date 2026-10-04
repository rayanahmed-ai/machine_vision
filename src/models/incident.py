from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class IncidentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class Incident(BaseModel):
    """Continuous security incident associated with one track."""

    incident_id: str
    track_id: str
    camera: str | None = None
    incident_type: str
    created_at: datetime
    last_updated: datetime
    zone: str | None = None
    status: IncidentStatus = IncidentStatus.ACTIVE
    associated_event_ids: list[str] = Field(default_factory=list)
