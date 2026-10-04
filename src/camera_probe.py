from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def probe_camera(url: str, timeout: float = 5.0) -> dict:
    """Probe an RTSP/HTTP camera URL and return a simple health report."""
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap.isOpened():
        return {"ok": False, "url": url, "error": "Could not open camera stream"}

    cap.set(cv2.CAP_PROP_POS_MSEC, 0)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        return {"ok": False, "url": url, "error": "Could not read a frame from the stream"}

    return {
        "ok": True,
        "url": url,
        "frame_shape": list(frame.shape),
        "width": int(frame.shape[1]),
        "height": int(frame.shape[0]),
        "channels": int(frame.shape[2]) if len(frame.shape) > 2 else 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe an IP camera or stream URL")
    parser.add_argument("url", nargs="?", default="rtsp://192.168.0.174:8554/stream", help="RTSP or HTTP URL to test")
    parser.add_argument("--timeout", type=float, default=5.0, help="timeout in seconds")
    args = parser.parse_args()

    result = probe_camera(args.url, timeout=args.timeout)
    print(result)
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
