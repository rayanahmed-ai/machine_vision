from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline import VisionPipeline


def run_demo() -> None:
    pipeline = VisionPipeline(
        {
            "camera_name": "front_door",
            "zones": {
                "entrance": {"polygon": [[0, 0], [1000, 0], [1000, 1000], [0, 1000]]},
                "restricted_area": {"polygon": [[250, 150], [650, 150], [650, 450], [250, 450]]},
            },
            "entrances": {"front_door": {"line": [[350, 100], [350, 500]]}},
            "loitering_threshold_seconds": 30,
            "tailgate_window_seconds": 3.0,
        }
    )

    base = datetime(2024, 1, 1, 10, 0, 0)
    observations = [
        {"camera": "front_door", "track_id": "100", "label": "person", "timestamp": (base).isoformat(), "position": (300, 200), "confidence": 0.9, "identity": "Rahul", "identity_status": "KNOWN", "identity_confidence": 0.94},
        {"camera": "front_door", "track_id": "100", "label": "person", "timestamp": (base + timedelta(seconds=1)).isoformat(), "position": (390, 220), "confidence": 0.9, "identity": "Rahul", "identity_status": "KNOWN", "identity_confidence": 0.94},
        {"camera": "front_door", "track_id": "101", "label": "person", "timestamp": (base + timedelta(seconds=1, milliseconds=400)).isoformat(), "position": (340, 220), "confidence": 0.82, "identity_status": "UNKNOWN", "identity_confidence": 0.2},
        {"camera": "front_door", "track_id": "101", "label": "person", "timestamp": (base + timedelta(seconds=2)).isoformat(), "position": (440, 220), "confidence": 0.82, "identity_status": "UNKNOWN", "identity_confidence": 0.2},
        {"camera": "front_door", "track_id": "101", "label": "person", "timestamp": (base + timedelta(seconds=10)).isoformat(), "position": (500, 300), "confidence": 0.82, "identity_status": "UNKNOWN", "identity_confidence": 0.2},
        {"camera": "front_door", "track_id": "101", "label": "person", "timestamp": (base + timedelta(seconds=20)).isoformat(), "position": (520, 310), "confidence": 0.82, "identity_status": "UNKNOWN", "identity_confidence": 0.2},
        {"camera": "front_door", "track_id": "101", "label": "person", "timestamp": (base + timedelta(seconds=40)).isoformat(), "position": (520, 310), "confidence": 0.82, "identity_status": "UNKNOWN", "identity_confidence": 0.2},
        {"camera": "front_door", "track_id": "101", "label": "person", "timestamp": (base + timedelta(seconds=50)).isoformat(), "position": (600, 350), "confidence": 0.82, "identity_status": "UNKNOWN", "identity_confidence": 0.2},
    ]

    for observation in observations:
        pipeline.process_observation(observation)

    print(json.dumps([event.model_dump() for event in pipeline.event_history()], indent=2, default=str))


if __name__ == "__main__":
    run_demo()
