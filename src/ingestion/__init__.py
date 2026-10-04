"""Ingestion adapters for external sensor feeds."""

from .frigate_listener import FrigateMQTTListener
from .normalizer import normalize_observation

__all__ = ["FrigateMQTTListener", "normalize_observation"]
