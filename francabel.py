#!/usr/bin/env python3
"""Francabel — overnight social desk for a local-services shop.

Run the desk (no GUI, for Task Scheduler):
    python francabel.py --run-desk

Open the desktop app:
    python francabel.py
    py francabel.py
    pyw francabel.py
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Francabel overnight social desk (local, no social login passwords)."
    )
    parser.add_argument(
        "--run-desk",
        action="store_true",
        help="Generate tonight's pack, append to the queue, and exit. No window.",
    )
    args = parser.parse_args(argv)
    if args.run_desk:
        from desk import run_desk

        path = run_desk()
        print(f"Francabel desk ran. Pack written: {path}")
        return 0
    from ui import start_gui

    start_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
