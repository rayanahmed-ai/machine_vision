from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.behavior.dwell_time import DwellTimeCalculator
from src.behavior.loitering import LoiteringEngine
from src.behavior.tailgating import TailgatingEngine
from src.context.context_engine import ContextEngine
from src.events.event_generator import build_event
from src.events.mqtt_publisher import MQTTEventPublisher
from src.incidents.manager import IncidentManager
from src.models.identity import IdentityStatus
from src.models.track import Track
from src.spatial.line_crossing import LineCrossingEngine
from src.spatial.zones import ZoneEngine

logger = logging.getLogger(__name__)

DEFAULT_ZONES = {
    "entrance": {"polygon": [[0, 0], [1000, 0], [1000, 1000], [0, 1000]]},
    "restricted_area": {"polygon": [[250, 150], [650, 150], [650, 450], [250, 450]]},
}
DEFAULT_ENTRANCES = {
    "front_door": {"line": [[350, 100], [350, 500]]},
}


class VisionPipeline:
    """Orchestrates observations into track updates, events, and publishing."""

    def __init__(self, config: dict[str, Any] | None = None, camera_name: str | None = None) -> None:
        self.config = config or {}
        self.camera_name = camera_name or self.config.get("camera_name", "camera-1")
        self.zones = self.config.get("zones", DEFAULT_ZONES)
        self.entrances = self.config.get("entrances", self.config.get("lines", DEFAULT_ENTRANCES))
        self.zone_engine = ZoneEngine(self.zones)
        self.line_engine = LineCrossingEngine(self.entrances)
        self.loitering_engine = LoiteringEngine({"zones": self.config.get("loitering_zones", {"entrance": {"threshold_seconds": self.config.get("loitering_threshold_seconds", 30)}, "restricted_area": {"threshold_seconds": self.config.get("loitering_threshold_seconds", 30)}}), "default_threshold_seconds": self.config.get("loitering_threshold_seconds", 30)})
        self.tailgating_engine = TailgatingEngine({"window_seconds": self.config.get("tailgate_window_seconds", self.config.get("tailgating_window_seconds", 3.0))})
        self.dwell_calculator = DwellTimeCalculator()
        self.context_engine = ContextEngine()
        self.incident_manager = IncidentManager()
        self.publisher = MQTTEventPublisher(
            host=self.config.get("mqtt_host", "localhost"),
            port=self.config.get("mqtt_port", 1883),
            output_topic=self.config.get("mqtt_output_topic", "home/vision/events"),
        )
        self.tracks: dict[str, Track] = {}
        self.event_log: list[Any] = []

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        if value is None:
            return datetime.now(timezone.utc)
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        if isinstance(value, str):
            candidate = value.replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(candidate).astimezone(timezone.utc)
            except ValueError:
                return datetime.now(timezone.utc)
        return datetime.now(timezone.utc)

    def process_observation(self, observation: dict[str, Any]) -> list[Any]:
        if not isinstance(observation, dict):
            logger.warning("Observation must be a mapping; got %s", type(observation).__name__)
            return []

        event_time = self._parse_timestamp(observation.get("timestamp"))
        track_id = str(observation.get("track_id") or observation.get("id") or "unknown")
        camera = str(observation.get("camera") or self.camera_name)
        position = observation.get("position")
        if not isinstance(position, (tuple, list)) or len(position) < 2:
            position = (0.0, 0.0)

        track = self.tracks.get(track_id)
        if track is None:
            track = Track(
                track_id=track_id,
                camera=camera,
                first_seen=event_time,
                last_seen=event_time,
                position=tuple(float(v) for v in position),
                previous_position=None,
                zone=None,
                previous_zone=None,
                identity_status=IdentityStatus.UNKNOWN,
                position_history=[tuple(float(v) for v in position)],
            )
            self.tracks[track_id] = track
            logger.info("Created track %s for camera %s", track_id, camera)
            self.event_log.append(build_event(event_type="person.tracked", camera=camera, track_id=track_id, confidence=float(observation.get("confidence", 0.0)), metadata={"source": "track_manager"}))

        previous_position = track.position
        track.previous_position = previous_position
        track.previous_zone = track.zone
        track.position = tuple(float(v) for v in position)
        if observation.get("identity") is not None:
            track.identity = str(observation["identity"])
        if observation.get("identity_status") is not None:
            raw_status = str(observation["identity_status"]).upper()
            if raw_status in {"KNOWN", "UNKNOWN", "AMBIGUOUS"}:
                track.identity_status = IdentityStatus(raw_status)
        if observation.get("identity_confidence") is not None:
            track.identity_confidence = float(observation["identity_confidence"])
        track.last_seen = event_time
        if track.first_seen is None:
            track.first_seen = track.last_seen

        if len(track.position_history) >= 100:
            track.position_history.pop(0)
        track.position_history.append(track.position)

        new_zone = self.zone_engine.get_zone_name(track.position)
        if new_zone != track.zone:
            track.previous_zone = track.zone
            track.zone = new_zone
            if new_zone is not None:
                track.entered_zone_at = track.last_seen
            self._record_zone_event(track, previous_position, track.position)

        if track.zone and track.entered_zone_at is not None:
            dwell_seconds = (track.last_seen - track.entered_zone_at).total_seconds()
            loiter = self.loitering_engine.evaluate(track.zone, dwell_seconds, event_time, identity=track.identity, nighttime=False)
            if loiter is not None and (track.last_loiter_event_at is None or (event_time - track.last_loiter_event_at).total_seconds() > 30):
                track.last_loiter_event_at = event_time
                event = build_event(
                    event_type="person.loitering",
                    camera=camera,
                    track_id=track_id,
                    zone=track.zone,
                    identity=track.identity,
                    identity_status=track.identity_status.value if hasattr(track.identity_status, "value") else str(track.identity_status),
                    identity_confidence=track.identity_confidence,
                    confidence=0.8,
                    metadata={"dwell_time": round(dwell_seconds, 2), "risk": loiter.risk_level, "nighttime": loiter.nighttime},
                )
                self.event_log.append(event)

        for entrance_name in self.entrances.keys():
            if self.line_engine.check_crossing(entrance_name, previous_position, track.position, event_time):
                event = build_event(
                    event_type="person.line_crossed",
                    camera=camera,
                    track_id=track_id,
                    zone=track.zone,
                    identity=track.identity,
                    identity_status=track.identity_status.value if hasattr(track.identity_status, "value") else str(track.identity_status),
                    identity_confidence=track.identity_confidence,
                    confidence=0.9,
                    metadata={"entrance": entrance_name, "side_changed": True},
                )
                self.event_log.append(event)
                if track.identity_status in {IdentityStatus.KNOWN, IdentityStatus.UNKNOWN, IdentityStatus.AMBIGUOUS}:
                    self.tailgating_engine.record_crossing(entrance_name, camera, track_id, event_time, track.identity_status.value)

        if track.identity_status == IdentityStatus.UNKNOWN:
            event = build_event(
                event_type="person.identity_unknown",
                camera=camera,
                track_id=track_id,
                zone=track.zone,
                identity=None,
                identity_status=track.identity_status.value,
                identity_confidence=track.identity_confidence,
                confidence=0.5,
                metadata={"reason": "no_identity_match"},
            )
            self.event_log.append(event)

        if track.identity_status == IdentityStatus.KNOWN and track.identity is not None:
            self.tailgating_engine.record_crossing("front_door", camera, track_id, event_time, "KNOWN")

        tailgating = self.tailgating_engine.detect("front_door", camera, track_id, event_time, track.identity_status.value if hasattr(track.identity_status, "value") else str(track.identity_status))
        if tailgating is not None and not track.metadata.get("tailgating_alerted"):
            track.metadata["tailgating_alerted"] = True
            event = build_event(
                event_type="person.tailgating_detected",
                camera=camera,
                track_id=track_id,
                zone=track.zone,
                identity=track.identity,
                identity_status=track.identity_status.value if hasattr(track.identity_status, "value") else str(track.identity_status),
                identity_confidence=track.identity_confidence,
                confidence=0.95,
                metadata={"authorized_person": tailgating.get("authorized_person"), "time_gap": tailgating.get("time_gap"), "risk": tailgating.get("risk")},
            )
            self.event_log.append(event)

        return list(self.event_log)

    def _record_zone_event(self, track: Track, previous_position: tuple[float, float] | None, current_position: tuple[float, float]) -> None:
        if track.previous_zone == track.zone:
            return
        event_type = "person.entered_zone" if track.zone else "person.left_zone"
        zone_name = track.zone or track.previous_zone
        event = build_event(
            event_type=event_type,
            camera=track.camera,
            track_id=track.track_id,
            zone=zone_name,
            identity=track.identity,
            identity_status=track.identity_status.value if hasattr(track.identity_status, "value") else str(track.identity_status),
            identity_confidence=track.identity_confidence,
            confidence=0.9,
            metadata={"previous_zone": track.previous_zone, "current_zone": track.zone, "position": list(current_position)},
        )
        self.event_log.append(event)

    def event_history(self) -> list[Any]:
        return list(self.event_log)

    def publish_events(self) -> None:
        self.publisher.publish_events([event for event in self.event_log if hasattr(event, "event_type")])
