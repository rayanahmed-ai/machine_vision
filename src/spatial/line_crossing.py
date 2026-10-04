from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class LineCrossingEngine:
    """Detect crossings across configured lines using side-of-line logic."""

    def __init__(self, entrances: dict[str, Any] | None = None) -> None:
        self.entrances = entrances or {}

    def _line(self, entrance_name: str) -> tuple[tuple[float, float], tuple[float, float]] | None:
        config = self.entrances.get(entrance_name)
        if not isinstance(config, dict):
            return None
        line = config.get("line")
        if not isinstance(line, (list, tuple)) or len(line) != 2:
            return None
        first = line[0]
        second = line[1]
        if not isinstance(first, (list, tuple)) or not isinstance(second, (list, tuple)):
            return None
        return (float(first[0]), float(first[1])), (float(second[0]), float(second[1]))

    def _side_of_line(self, point: tuple[float, float], line: tuple[tuple[float, float], tuple[float, float]]) -> float:
        p1, p2 = line
        x, y = point
        return (p2[0] - p1[0]) * (y - p1[1]) - (p2[1] - p1[1]) * (x - p1[0])

    def check_crossing(self, entrance_name: str, previous_position: tuple[float, float] | None, current_position: tuple[float, float] | None, timestamp: datetime) -> bool:
        if previous_position is None or current_position is None:
            return False
        line = self._line(entrance_name)
        if line is None:
            return False

        previous_side = self._side_of_line(previous_position, line)
        current_side = self._side_of_line(current_position, line)
        if previous_side == 0 or current_side == 0:
            return False
        return previous_side * current_side < 0
