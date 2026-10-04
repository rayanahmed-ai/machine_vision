from __future__ import annotations

import json
import logging
from typing import Any

from src.models.vision_event import VisionEvent

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import paho.mqtt.client as mqtt
except Exception:  # pragma: no cover
    mqtt = None


class MQTTEventPublisher:
    """Publishes VisionEvent payloads to the configured MQTT output topic."""

    def __init__(self, host: str = "localhost", port: int | None = 1883, output_topic: str = "home/vision/events") -> None:
        self.host = host or "localhost"
        self.port = int(port if port is not None else 1883)
        self.output_topic = output_topic
        self.client = None
        if mqtt is not None:
            self.client = mqtt.Client()
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client: Any, userdata: Any, flags: Any, rc: int) -> None:
        logger.info("Connected to MQTT output broker %s:%s (rc=%s)", self.host, self.port, rc)

    def _on_disconnect(self, client: Any, userdata: Any, rc: int) -> None:
        logger.warning("Published MQTT output disconnected from %s:%s (rc=%s)", self.host, self.port, rc)

    def connect(self) -> None:
        if self.client is None:
            logger.warning("MQTT output disabled: paho-mqtt is not installed")
            return
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

    def publish_event(self, event: VisionEvent) -> bool:
        if self.client is None:
            logger.warning("Skipping MQTT publish for event %s because the broker is unavailable", event.event_type)
            return False
        payload = json.dumps(event.model_dump(), default=str)
        self.client.publish(self.output_topic, payload, qos=1)
        logger.debug("Published event %s to %s", event.event_type, self.output_topic)
        return True

    def publish_events(self, events: list[VisionEvent]) -> None:
        for event in events:
            self.publish_event(event)

    def close(self) -> None:
        if self.client is not None:
            self.client.disconnect()
            self.client.loop_stop()
