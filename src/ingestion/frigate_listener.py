from __future__ import annotations

import json
import logging
from typing import Any

from src.ingestion.normalizer import normalize_observation

logger = logging.getLogger(__name__)

try:  # pragma: no cover - depends on runtime install
    import paho.mqtt.client as mqtt
except Exception:  # pragma: no cover
    mqtt = None


class FrigateMQTTListener:
    """Consumes Frigate events from MQTT and forwards normalized observations."""

    def __init__(self, pipeline: Any, mqtt_host: str = "localhost", mqtt_port: int = 1883, topic: str = "frigate/events") -> None:
        self.pipeline = pipeline
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.topic = topic
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        if mqtt is None:
            logger.warning("paho-mqtt is not installed; MQTT listener disabled")
            return

        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client: Any, userdata: Any, flags: Any, rc: int) -> None:
        logger.info("Connected to MQTT broker %s:%s with code %s", self.mqtt_host, self.mqtt_port, rc)
        client.subscribe(self.topic)

    def _on_disconnect(self, client: Any, userdata: Any, rc: int) -> None:
        logger.warning("MQTT disconnected from %s:%s with rc=%s", self.mqtt_host, self.mqtt_port, rc)

    def _on_message(self, client: Any, userdata: Any, message: Any) -> None:
        try:
            payload = json.loads(message.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            logger.warning("Ignoring malformed MQTT payload on %s", self.topic)
            return

        if not isinstance(payload, dict):
            logger.warning("Ignoring non-dictionary payload on %s", self.topic)
            return

        label = str(payload.get("label") or payload.get("type") or "").lower()
        if label and label != "person":
            logger.debug("Ignoring non-person Frigate message: %s", label)
            return

        try:
            normalized = normalize_observation(payload, camera=self.pipeline.camera_name if hasattr(self.pipeline, "camera_name") else None)
        except ValueError as exc:
            logger.warning("Malformed Frigate observation ignored: %s", exc)
            return

        self.pipeline.process_observation(normalized)

    def start(self) -> None:
        if self.client is None:
            logger.warning("MQTT listener not available because paho-mqtt is absent")
            return
        self.client.connect(self.mqtt_host, self.mqtt_port, 60)
        self.client.loop_forever()

    def stop(self) -> None:
        if self.client is not None:
            self.client.disconnect()
