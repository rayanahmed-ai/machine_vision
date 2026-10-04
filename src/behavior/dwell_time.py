from __future__ import annotations

from datetime import datetime


class DwellTimeCalculator:
    """Calculate track and zone dwell durations from timestamps."""

    def __init__(self) -> None:
        self.zone_starts: dict[str, datetime] = {}

    def total_track_duration(self, start: datetime, end: datetime) -> float:
        return max(0.0, (end - start).total_seconds())

    def calculate_dwell(self, start: datetime, end: datetime) -> float:
        return self.total_track_duration(start, end)

    def zone_duration(self, zone_name: str, start: datetime, end: datetime) -> float:
        return self.calculate_dwell(start, end)

    def record_zone_entry(self, zone_name: str, timestamp: datetime) -> None:
        self.zone_starts[zone_name] = timestamp

    def get_zone_dwell(self, zone_name: str, timestamp: datetime) -> float:
        start = self.zone_starts.get(zone_name)
        if start is None:
            return 0.0
        return max(0.0, (timestamp - start).total_seconds())
