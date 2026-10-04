from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


@dataclass
class Settings:
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic: str = "frigate/events"
    mqtt_output_topic: str = "home/vision/events"
    loiter_threshold_seconds: float = 30.0
    tailgate_window_seconds: float = 3.0
    compreface_url: str = "http://localhost:8000"
    compreface_api_key: str = ""
    compreface_min_similarity: float = 0.8
    cameras: dict[str, Any] = field(default_factory=dict)
    zones: dict[str, Any] = field(default_factory=dict)
    thresholds: dict[str, Any] = field(default_factory=dict)
    lines: dict[str, Any] = field(default_factory=dict)


def load_settings() -> Settings:
    config_root = ROOT / "config"
    cameras_cfg = _read_yaml(config_root / "cameras.yaml")
    zones_cfg = _read_yaml(config_root / "zones.yaml")
    thresholds_cfg = _read_yaml(config_root / "thresholds.yaml")

    settings = Settings(
        mqtt_host=os.getenv("MQTT_HOST", "localhost"),
        mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
        mqtt_topic=os.getenv("MQTT_TOPIC", "frigate/events"),
        mqtt_output_topic=os.getenv("MQTT_OUTPUT_TOPIC", "home/vision/events"),
        loiter_threshold_seconds=float(os.getenv("LOITER_THRESHOLD_SECONDS", thresholds_cfg.get("loiter_threshold_seconds", 30.0))),
        tailgate_window_seconds=float(os.getenv("TAILGATE_WINDOW_SECONDS", thresholds_cfg.get("tailgate_window_seconds", 3.0))),
        compreface_url=os.getenv("COMPREFACE_URL", "http://localhost:8000"),
        compreface_api_key=os.getenv("COMPREFACE_API_KEY", ""),
        compreface_min_similarity=float(os.getenv("COMPREFACE_MIN_SIMILARITY", thresholds_cfg.get("compreface_min_similarity", 0.8))),
        cameras=cameras_cfg.get("cameras", cameras_cfg),
        zones=zones_cfg.get("zones", zones_cfg),
        thresholds=thresholds_cfg,
        lines=(zones_cfg.get("entrances", {}) if isinstance(zones_cfg, dict) else {}),
    )
    return settings
