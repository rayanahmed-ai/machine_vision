from datetime import datetime, timedelta

from src.behavior.tailgating import TailgatingEngine


def test_known_followed_by_unknown():
    engine = TailgatingEngine({"window_seconds": 3.0})
    now = datetime.utcnow()
    engine.record_crossing("front_door", "cam1", "track-1", now, "known")
    event = engine.detect("front_door", "cam1", "track-2", now + timedelta(seconds=1.5), "unknown")
    assert event is not None
    assert event["track_id"] == "track-2"


def test_known_followed_by_known():
    engine = TailgatingEngine({"window_seconds": 3.0})
    now = datetime.utcnow()
    engine.record_crossing("front_door", "cam1", "track-1", now, "known")
    assert engine.detect("front_door", "cam1", "track-2", now + timedelta(seconds=1.5), "known") is None


def test_unknown_followed_by_unknown():
    engine = TailgatingEngine({"window_seconds": 3.0})
    now = datetime.utcnow()
    engine.record_crossing("front_door", "cam1", "track-1", now, "unknown")
    assert engine.detect("front_door", "cam1", "track-2", now + timedelta(seconds=1.5), "unknown") is None


def test_crossing_outside_time_window():
    engine = TailgatingEngine({"window_seconds": 3.0})
    now = datetime.utcnow()
    engine.record_crossing("front_door", "cam1", "track-1", now, "known")
    assert engine.detect("front_door", "cam1", "track-2", now + timedelta(seconds=5), "unknown") is None


def test_different_camera():
    engine = TailgatingEngine({"window_seconds": 3.0})
    now = datetime.utcnow()
    engine.record_crossing("front_door", "cam1", "track-1", now, "known")
    assert engine.detect("front_door", "cam2", "track-2", now + timedelta(seconds=1.5), "unknown") is None


def test_different_entrance():
    engine = TailgatingEngine({"window_seconds": 3.0})
    now = datetime.utcnow()
    engine.record_crossing("front_door", "cam1", "track-1", now, "known")
    assert engine.detect("back_door", "cam1", "track-2", now + timedelta(seconds=1.5), "unknown") is None


def test_same_track_id():
    engine = TailgatingEngine({"window_seconds": 3.0})
    now = datetime.utcnow()
    engine.record_crossing("front_door", "cam1", "track-1", now, "known")
    assert engine.detect("front_door", "cam1", "track-1", now + timedelta(seconds=1.5), "unknown") is None
