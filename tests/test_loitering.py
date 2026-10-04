from datetime import datetime, timedelta

from src.behavior.loitering import LoiteringEngine


def test_normal_movement():
    engine = LoiteringEngine({"zones": {"entrance": {"threshold_seconds": 30}}, "nighttime": False})
    result = engine.evaluate("entrance", 10, datetime.utcnow(), identity="unknown")
    assert result is None


def test_entrance_loitering():
    engine = LoiteringEngine({"zones": {"entrance": {"threshold_seconds": 30}}, "nighttime": False})
    result = engine.evaluate("entrance", 35, datetime.utcnow(), identity="unknown")
    assert result is not None
    assert result.zone == "entrance"


def test_restricted_area_loitering():
    engine = LoiteringEngine({"zones": {"restricted_area": {"threshold_seconds": 20}}, "nighttime": False})
    result = engine.evaluate("restricted_area", 25, datetime.utcnow(), identity="known")
    assert result is not None
    assert result.zone == "restricted_area"
