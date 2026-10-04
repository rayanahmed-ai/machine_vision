from datetime import datetime

from src.spatial.line_crossing import LineCrossingEngine


def test_crossing_left_to_right():
    engine = LineCrossingEngine({
        "front_door": {"line": [[350, 100], [350, 500]]}
    })

    assert engine.check_crossing("front_door", (300, 200), (400, 300), datetime.utcnow()) is True


def test_crossing_right_to_left():
    engine = LineCrossingEngine({
        "front_door": {"line": [[350, 100], [350, 500]]}
    })
    assert engine.check_crossing("front_door", (400, 300), (300, 200), datetime.utcnow()) is True


def test_no_crossing():
    engine = LineCrossingEngine({
        "front_door": {"line": [[350, 100], [350, 500]]}
    })
    assert engine.check_crossing("front_door", (300, 200), (320, 250), datetime.utcnow()) is False
