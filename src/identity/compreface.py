from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np
import requests

from src.models.identity import IdentityStatus

logger = logging.getLogger(__name__)


@dataclass
class IdentityResult:
    status: IdentityStatus
    identity: str | None
    confidence: float = 0.0


def crop_person_region(frame: Any, bbox: tuple[float, float, float, float] | list[float], padding: int = 20) -> Any:
    """Create a tight crop around a detected person box."""
    if frame is None:
        raise ValueError("frame cannot be None")
    if not isinstance(bbox, (tuple, list)) or len(bbox) != 4:
        raise ValueError("bbox must contain x, y, w, h")
    x, y, w, h = [float(v) for v in bbox]
    height, width = frame.shape[:2]
    x1 = max(0, int(x) - padding)
    y1 = max(0, int(y) - padding)
    x2 = min(width, int(x + w) + padding)
    y2 = min(height, int(y + h) + padding)
    return frame[y1:y2, x1:x2]


class CompreFaceAdapter:
    """Thin adapter over the CompreFace REST API."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "", min_similarity: float = 0.8) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.min_similarity = float(min_similarity)

    def recognize(self, image_bytes: bytes, subject: str | None = None) -> IdentityResult:
        """Recognize the face in an image and map it to a domain status."""
        if not image_bytes:
            return IdentityResult(status=IdentityStatus.UNKNOWN, identity=None, confidence=0.0)

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/recognition/recognize",
                files={"file": ("face.jpg", image_bytes, "image/jpeg")},
                headers={"x-api-key": self.api_key},
                timeout=5,
            )
        except requests.RequestException as exc:
            logger.warning("CompreFace API unavailable: %s", exc)
            return IdentityResult(status=IdentityStatus.UNKNOWN, identity=None, confidence=0.0)

        if response.status_code >= 500:
            logger.warning("CompreFace API returned %s", response.status_code)
            return IdentityResult(status=IdentityStatus.UNKNOWN, identity=None, confidence=0.0)

        try:
            payload = response.json()
        except ValueError:
            logger.warning("Malformed response from CompreFace")
            return IdentityResult(status=IdentityStatus.UNKNOWN, identity=None, confidence=0.0)

        candidates = payload.get("result") or payload.get("faces") or []
        if not candidates:
            return IdentityResult(status=IdentityStatus.UNKNOWN, identity=None, confidence=0.0)

        best = candidates[0]
        best_label = best.get("subject") or best.get("name") or best.get("label")
        best_confidence = float(best.get("similarity") or best.get("confidence") or 0.0)

        if best_label is None and best_confidence <= 0:
            return IdentityResult(status=IdentityStatus.UNKNOWN, identity=None, confidence=0.0)

        if best_confidence < self.min_similarity:
            return IdentityResult(status=IdentityStatus.UNKNOWN, identity=best_label, confidence=best_confidence)

        return IdentityResult(status=IdentityStatus.KNOWN, identity=str(best_label), confidence=best_confidence)
