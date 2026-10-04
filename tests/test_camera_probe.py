from src.camera_probe import probe_camera


def test_probe_camera_handles_bad_url():
    result = probe_camera("rtsp://127.0.0.1:1/stream", timeout=1.0)
    assert result["ok"] is False
    assert "error" in result
