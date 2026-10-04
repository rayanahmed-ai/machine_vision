from src.models.vision_event import VisionEvent


def test_event_schema():
    event = VisionEvent(
        event_type="person.entered_zone",
        timestamp="2024-01-01T00:00:00Z",
        camera="front_door",
        track_id="42",
        zone="entrance",
        identity="Rahul",
        identity_status="KNOWN",
        identity_confidence=0.94,
        confidence=0.9,
        metadata={"risk": "LOW"},
    )
    assert event.event_type == "person.entered_zone"
    assert event.camera == "front_door"
