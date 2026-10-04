from fastapi.testclient import TestClient

from src.api import app


def test_rest_api_accepts_observation():
    client = TestClient(app)
    response = client.post(
        "/api/v1/observations",
        json={
            "camera": "cam1",
            "track_id": "42",
            "label": "person",
            "timestamp": "2024-01-01T00:00:00Z",
            "position": [200, 200],
            "confidence": 0.9,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert "events" in payload
    assert any(event["event_type"] == "person.tracked" for event in payload["events"])
