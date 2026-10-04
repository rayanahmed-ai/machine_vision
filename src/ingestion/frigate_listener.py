from __future__ import annotations

import logging
import threading
from typing import Any

import requests

from src.ingestion.normalizer import normalize_observation

logger = logging.getLogger(__name__)


class FrigateRESTListener:
    """Polls a Frigate REST API for event payloads and forwards normalized observations."""

    def __init__(self, pipeline: Any, restapi_url: str = "http://localhost:5000", api_key: str | None = None, poll_interval: float = 5.0) -> None:
        self.pipeline = pipeline
        self.restapi_url = (restapi_url or "").rstrip("/")
        self.api_key = api_key
        self.poll_interval = poll_interval
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _fetch_events(self) -> list[dict[str, Any]]:
        if not self.restapi_url:
            logger.warning("Frigate REST listener disabled: no URL configured")
            return []

        url = f"{self.restapi_url}/api/events"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Frigate REST poll failed for %s: %s", url, exc)
            return []

        payload = response.json()
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            for key in ("events", "data", "items"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []

    def _process_event(self, payload: dict[str, Any]) -> None:
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
        if not self.restapi_url:
            logger.warning("Frigate REST listener not available because the URL is absent")
            return
        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def _poll_loop(self) -> None:
        while not self._stop_event.is_set():
            for event in self._fetch_events():
                self._process_event(event)
            self._stop_event.wait(self.poll_interval)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
