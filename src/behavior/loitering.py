from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class LoiteringResult:
    zone: str
    dwell_time: float
    identity: str | None
    nighttime: bool
    risk_level: str


class LoiteringEngine:
    """Loitering is detected when a track remains in a security-sensitive zone too long."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.zones = self.config.get("zones", {})
        self.default_threshold = float(self.config.get("default_threshold_seconds", self.config.get("threshold_seconds", 30.0)))

    def _threshold_for(self, zone: str) -> float:
        zone_config = self.zones.get(zone, {}) if isinstance(self.zones, dict) else {}
        if isinstance(zone_config, dict):
            return float(zone_config.get("threshold_seconds", zone_config.get("threshold", self.default_threshold)))
        return self.default_threshold

    def evaluate(self, zone: str, dwell_seconds: float, timestamp: datetime | None = None, identity: str | None = None, nighttime: bool = False) -> LoiteringResult | None:
        threshold = self._threshold_for(zone)
        if dwell_seconds <= threshold:
            return None
        return LoiteringResult(
            zone=zone,
            dwell_time=float(dwell_seconds),
            identity=identity,
            nighttime=nighttime,
            risk_level="HIGH" if nighttime else "MEDIUM",
        )
