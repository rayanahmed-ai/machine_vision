from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI

from src.config import load_settings
from src.pipeline import DEFAULT_ENTRANCES, DEFAULT_ZONES, VisionPipeline


def create_pipeline() -> VisionPipeline:
    settings = load_settings()
    config: dict[str, Any] = {
        "camera_name": "front_door",
        "zones": settings.zones or DEFAULT_ZONES,
        "entrances": settings.lines or DEFAULT_ENTRANCES,
        "loitering_threshold_seconds": settings.loiter_threshold_seconds,
        "tailgate_window_seconds": settings.tailgate_window_seconds,
        "mqtt_host": settings.mqtt_host,
        "mqtt_port": settings.mqtt_port,
        "mqtt_output_topic": settings.mqtt_output_topic,
    }
    if os.getenv("MQTT_HOST") is None and os.getenv("MQTT_PORT") is None:
        config["mqtt_host"] = None
        config["mqtt_port"] = None
    return VisionPipeline(config)


pipeline = create_pipeline()
app = FastAPI(title="Machine Vision API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok"}


@app.get("/api/v1/events")
def list_events() -> dict[str, Any]:
    return {
        "events": [event.model_dump(mode="json", exclude_none=True) for event in pipeline.event_history()],
        "count": len(pipeline.event_history()),
    }


@app.post("/api/v1/observations")
def ingest_observation(observation: dict[str, Any]) -> dict[str, Any]:
    events = pipeline.process_observation(observation)
    return {
        "accepted": True,
        "events": [event.model_dump(mode="json", exclude_none=True) for event in events],
    }


@app.post("/api/v1/batch")
def ingest_batch(observations: list[dict[str, Any]]) -> dict[str, Any]:
    all_events: list[dict[str, Any]] = []
    for observation in observations:
        emitted = pipeline.process_observation(observation)
        all_events.extend(event.model_dump(mode="json", exclude_none=True) for event in emitted)
    return {"accepted": True, "count": len(observations), "events": all_events}
