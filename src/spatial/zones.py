from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ZoneEngine:
    """Identify the zone containing a person based on polygon geometry."""

    def __init__(self, zones: dict[str, Any] | None = None, config_path: str | Path | None = None) -> None:
        self.zones = zones or {}
        self.config_path = Path(config_path) if config_path else None
        if not self.zones and self.config_path and self.config_path.exists():
            import yaml

            with self.config_path.open("r", encoding="utf-8") as handle:
                loaded = yaml.safe_load(handle) or {}
            self.zones = loaded.get("zones", loaded)
        self._cache: dict[str, np.ndarray] = {}
        for name, zone_config in self.zones.items():
            polygon = zone_config.get("polygon") if isinstance(zone_config, dict) else zone_config
            if polygon is not None:
                self._cache[name] = np.array(polygon, dtype=np.float32)

    def get_zone_name(self, point: tuple[float, float] | list[float]) -> str | None:
        if not self.zones:
            return None
        x, y = float(point[0]), float(point[1])
        matches: list[tuple[int, str]] = []
        for name, polygon in self.zones.items():
            coords = polygon.get("polygon") if isinstance(polygon, dict) else polygon
            if coords is None:
                continue
            array = np.array(coords, dtype=np.float32)
            if cv2.pointPolygonTest(array, (x, y), False) >= 0:
                area = abs(cv2.contourArea(array.reshape(-1, 1, 2)))
                matches.append((int(area), name))
        if not matches:
            return None
        _, name = min(matches, key=lambda item: item[0])
        return name

    def zone_transition(self, previous_zone: str | None, current_zone: str | None) -> str | None:
        if previous_zone == current_zone:
            return None
        if previous_zone and current_zone:
            return "changed"
        if current_zone:
            return "entered"
        if previous_zone:
            return "left"
        return None

    def contains(self, zone_name: str, point: tuple[float, float]) -> bool:
        zone = self.zones.get(zone_name)
        if zone is None:
            return False
        polygon = zone.get("polygon") if isinstance(zone, dict) else zone
        if polygon is None:
            return False
        array = np.array(polygon, dtype=np.float32)
        return bool(cv2.pointPolygonTest(array, (float(point[0]), float(point[1])), False) >= 0)
