from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.demo import run_demo

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Machine Vision subsystem")
    parser.add_argument("--demo", action="store_true", help="run the offline demo")
    parser.add_argument("--rest", action="store_true", help="run the HTTP REST API")
    args = parser.parse_args()
    if args.demo:
        run_demo()
        return
    if args.rest:
        import uvicorn

        host = os.getenv("REST_HOST", "0.0.0.0")
        port = int(os.getenv("REST_PORT", "8000"))
        uvicorn.run("src.api:app", host=host, port=port, reload=False)
        return
    print("Machine Vision service started. Use --demo for the synthetic demo or --rest for the HTTP API.")


if __name__ == "__main__":
    main()
