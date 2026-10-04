from __future__ import annotations

import logging

import requests

from src.models.vision_event import VisionEvent

logger = logging.getLogger(__name__)


class RestEventPublisher:
    """Publishes VisionEvent payloads to a REST API endpoint."""

    def __init__(self, url: str | None = None, **kwargs: object) -> None:
        self.url = (url or "").rstrip("/")
        self.timeout = float(kwargs.get("timeout", 5.0))

    def connect(self) -> None:
        if not self.url:
            logger.warning("REST output disabled: no endpoint configured")

    def publish_event(self, event: VisionEvent) -> bool:
        if not self.url:
            logger.warning("Skipping REST publish for event %s because no endpoint is configured", event.event_type)
            return False

        payload = event.model_dump(mode="json", exclude_none=True)
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("REST publish failed for event %s: %s", event.event_type, exc)
            return False

        logger.debug("Published event %s to %s", event.event_type, self.url)
        return True

    def publish_events(self, events: list[VisionEvent]) -> None:
        for event in events:
            self.publish_event(event)

    def close(self) -> None:
        return None
