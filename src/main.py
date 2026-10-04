from __future__ import annotations

import argparse
import logging
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
    args = parser.parse_args()
    if args.demo:
        run_demo()
        return
    print("Machine Vision service started. Use --demo to run the synthetic demo.")


if __name__ == "__main__":
    main()
