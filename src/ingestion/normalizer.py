from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_timestamp(value: Any) -> str:
    if value is None:
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"
    if isinstance(value, datetime):
        return value.isoformat(timespec="seconds") + "Z"
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat().replace("+00:00", "Z")
        except ValueError:
            return value
    return str(value)


def _extract_position(raw: dict[str, Any]) -> tuple[float, float] | None:
    if not isinstance(raw, dict):
        return None
    for key in ("position", "center", "centroid", "coords", "location"):
        position = raw.get(key)
        if isinstance(position, (list, tuple)) and len(position) >= 2:
            return (_coerce_float(position[0]), _coerce_float(position[1]))
    for key in ("x", "y"):
        if key in raw and "y" in raw:
            return (_coerce_float(raw.get("x")), _coerce_float(raw.get("y")))
    return None


def normalize_observation(raw_payload: Any, camera: str | None = None) -> dict[str, Any]:
    """Convert a Frigate event into a defensive internal observation."""
    if not isinstance(raw_payload, dict):
        raise ValueError("fright payload must be a dictionary")

    label = raw_payload.get("label") or raw_payload.get("type") or "person"
    if isinstance(label, str):
        label = label.lower()

    track_id = raw_payload.get("track_id")
    if track_id is None:
        track_id = raw_payload.get("id") or raw_payload.get("tracker_id") or raw_payload.get("track")

    if track_id is None:
        raise ValueError("missing track_id in observation")

    position = _extract_position(raw_payload)
    confidence = raw_payload.get("confidence")
    if confidence is None:
        confidence = raw_payload.get("score") or raw_payload.get("similarity") or 0.0

    zone = raw_payload.get("zone") or raw_payload.get("current_zone") or raw_payload.get("zone_name")
    timestamp = raw_payload.get("timestamp") or raw_payload.get("event_time") or raw_payload.get("created_at")

    observation = {
        "camera": str(camera or raw_payload.get("camera") or raw_payload.get("camera_name") or "unknown"),
        "track_id": str(track_id),
        "label": str(label),
        "timestamp": _normalize_timestamp(timestamp),
        "position": position,
        "zone": zone,
        "confidence": _coerce_float(confidence, 0.0),
        "raw_payload": raw_payload,
    }
    logger.debug("Normalized Frigate observation for %s/%s", observation["camera"], observation["track_id"])
    return observation
