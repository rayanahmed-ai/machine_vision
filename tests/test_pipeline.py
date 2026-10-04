from src.pipeline import VisionPipeline


def test_pipeline_generates_zone_and_line_events():
    pipeline = VisionPipeline({"loitering_threshold_seconds": 30, "tailgate_window_seconds": 3})

    for obs in [
        {"camera": "cam1", "track_id": "42", "label": "person", "timestamp": "2024-01-01T00:00:00Z", "position": (200, 200), "confidence": 0.9},
        {"camera": "cam1", "track_id": "42", "label": "person", "timestamp": "2024-01-01T00:00:05Z", "position": (250, 240), "confidence": 0.9},
        {"camera": "cam1", "track_id": "42", "label": "person", "timestamp": "2024-01-01T00:00:10Z", "position": (320, 300), "confidence": 0.9},
    ]:
        pipeline.process_observation(obs)

    events = pipeline.event_history()
    assert len(events) >= 1
    assert any(event.event_type in {"person.entered_zone", "person.line_crossed"} for event in events)
