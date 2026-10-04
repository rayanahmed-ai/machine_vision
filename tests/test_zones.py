from src.spatial.zones import ZoneEngine


def test_point_inside_zone():
    zone_engine = ZoneEngine({
        "entrance": {
            "polygon": [[100, 100], [700, 100], [700, 500], [100, 500]],
        }
    })
    assert zone_engine.get_zone_name((200, 200)) == "entrance"


def test_point_outside_zone():
    zone_engine = ZoneEngine({
        "entrance": {
            "polygon": [[100, 100], [700, 100], [700, 500], [100, 500]],
        }
    })
    assert zone_engine.get_zone_name((50, 50)) is None


def test_zone_transition():
    zone_engine = ZoneEngine({
        "entrance": {"polygon": [[100, 100], [700, 100], [700, 500], [100, 500]]},
        "restricted": {"polygon": [[250, 150], [650, 150], [650, 450], [250, 450]]},
    })
    assert zone_engine.get_zone_name((50, 50)) is None
    assert zone_engine.get_zone_name((300, 300)) == "restricted"
