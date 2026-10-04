from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from src.models.incident import Incident, IncidentStatus

logger = logging.getLogger(__name__)


class IncidentManager:
    """Tracks active incidents per track and closes them once they end."""

    def __init__(self) -> None:
        self.active_by_track: dict[str, Incident] = {}

    def open_incident(self, *, track_id: str, camera: str | None, incident_type: str, zone: str | None, event_id: str | None = None) -> Incident:
        timestamp = datetime.utcnow()
        incident = Incident(
            incident_id=f"inc-{track_id}-{timestamp.strftime('%Y%m%d%H%M%S')}",
            track_id=track_id,
            camera=camera,
            incident_type=incident_type,
            created_at=timestamp,
            last_updated=timestamp,
            zone=zone,
            status=IncidentStatus.ACTIVE,
            associated_event_ids=[event_id] if event_id else [],
        )
        self.active_by_track[track_id] = incident
        logger.info("Opened %s incident for track %s", incident_type, track_id)
        return incident

    def update_incident(self, *, track_id: str, zone: str | None = None, event_id: str | None = None) -> Incident | None:
        incident = self.active_by_track.get(track_id)
        if incident is None:
            return None
        incident.last_updated = datetime.utcnow()
        if zone is not None:
            incident.zone = zone
        if event_id is not None and event_id not in incident.associated_event_ids:
            incident.associated_event_ids.append(event_id)
        return incident

    def close_incident(self, track_id: str) -> Incident | None:
        incident = self.active_by_track.pop(track_id, None)
        if incident is None:
            return None
        incident.status = IncidentStatus.CLOSED
        incident.last_updated = datetime.utcnow()
        logger.info("Closed incident for track %s", track_id)
        return incident
