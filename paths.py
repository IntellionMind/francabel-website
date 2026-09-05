"""Folders for Francabel. App data lives next to the script when writable, else ~/.francabel."""

from __future__ import annotations

import os
import sys


def app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _writable(folder: str) -> bool:
    try:
        os.makedirs(folder, exist_ok=True)
        probe = os.path.join(folder, ".write-probe")
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("ok")
        os.remove(probe)
        return True
    except OSError:
        return False


def data_dir() -> str:
    local = os.path.join(app_dir(), "data")
    if _writable(local):
        return local
    home = os.path.join(os.path.expanduser("~"), ".francabel")
    os.makedirs(home, exist_ok=True)
    return home


def assets_dir() -> str:
    return os.path.join(app_dir(), "assets")


def packs_dir() -> str:
    d = os.path.join(data_dir(), "packs")
    os.makedirs(d, exist_ok=True)
    return d


def export_dir() -> str:
    d = os.path.join(data_dir(), "export")
    os.makedirs(d, exist_ok=True)
    return d


def generated_dir() -> str:
    d = os.path.join(data_dir(), "generated")
    os.makedirs(d, exist_ok=True)
    return d


def shop_path() -> str:
    return os.path.join(data_dir(), "shop.json")


def queue_path() -> str:
    return os.path.join(data_dir(), "queue.json")


def pack_path(day: str) -> str:
    return os.path.join(packs_dir(), f"{day}.json")
