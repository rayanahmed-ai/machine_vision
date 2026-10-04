from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class TailgatingEngine:
    """Detect a person crossing behind an authorized person within a short gap."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.window_seconds = float((config or {}).get("window_seconds", 3.0))
        self.history: deque[dict[str, Any]] = deque(maxlen=200)

    def record_crossing(self, entrance: str, camera: str, track_id: str, timestamp: datetime, identity_status: str | None) -> None:
        self.history.append(
            {
                "entrance": entrance,
                "camera": camera,
                "track_id": track_id,
                "timestamp": timestamp,
                "identity_status": (identity_status or "UNKNOWN").upper(),
            }
        )

    def detect(self, entrance: str, camera: str, track_id: str, timestamp: datetime, identity_status: str | None) -> dict[str, Any] | None:
        status = (identity_status or "UNKNOWN").upper()
        if status not in {"UNKNOWN", "AMBIGUOUS"}:
            return None
        for prior in reversed(self.history):
            if prior["track_id"] == track_id:
                continue
            if prior["camera"] != camera or prior["entrance"] != entrance:
                continue
            time_gap = (timestamp - prior["timestamp"]).total_seconds()
            if time_gap <= 0 or time_gap > self.window_seconds:
                continue
            if prior["identity_status"] != "KNOWN":
                continue
            logger.debug("Tailgating detected between %s and %s on %s/%s", prior["track_id"], track_id, camera, entrance)
            return {
                "track_id": track_id,
                "camera": camera,
                "entrance": entrance,
                "authorized_person": prior["track_id"],
                "time_gap": round(time_gap, 3),
                "risk": "HIGH",
            }
        return None
