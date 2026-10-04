"""Ingestion adapters for external sensor feeds."""

from .frigate_listener import FrigateRESTListener
from .normalizer import normalize_observation

__all__ = ["FrigateRESTListener", "normalize_observation"]
