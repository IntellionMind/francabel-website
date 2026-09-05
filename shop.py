"""Shop settings. The honesty lock is a constant — it cannot be turned off."""

from __future__ import annotations

import json
from typing import Any

from paths import shop_path

CORE_SERVICES = [
    "Water heater replacement",
    "Basketball hoop installation",
    "Catering / parties",
    "Government contracts",
]

HONESTY_LOCK = (
    "Honesty lock (cannot be turned off): this desk will not invent named "
    "customers, families, or testimonials. Generated scenes are labeled COMPOSITE. "
    "Francabel never stores Facebook, Instagram, TikTok, or LinkedIn login passwords."
)

DEFAULT_SHOP: dict[str, Any] = {
    "name": "Francabel",
    "cities": [],
    "desk_hour": "3:00",
    "posts_per_night": 2,
    "extra_platforms": [],
    "extra_services": [],
    "facebook_page_token": "",
    "linkedin_token": "",
    "website": "https://francabel.com",
}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def load_shop() -> dict[str, Any]:
    path = shop_path()
    data = dict(DEFAULT_SHOP)
    try:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
        if isinstance(raw, dict):
            data.update(raw)
    except (OSError, json.JSONDecodeError):
        pass
    data["name"] = str(data.get("name") or "Francabel").strip() or "Francabel"
    data["cities"] = _as_list(data.get("cities"))
    data["desk_hour"] = str(data.get("desk_hour") or "3:00").strip() or "3:00"
    try:
        n = int(data.get("posts_per_night") or 2)
    except (TypeError, ValueError):
        n = 2
    data["posts_per_night"] = min(3, max(1, n))
    data["extra_platforms"] = _as_list(data.get("extra_platforms"))
    data["extra_services"] = _as_list(data.get("extra_services"))
    data["facebook_page_token"] = str(data.get("facebook_page_token") or "").strip()
    data["linkedin_token"] = str(data.get("linkedin_token") or "").strip()
    data["website"] = str(data.get("website") or "https://francabel.com").strip() or "https://francabel.com"
    # Never persist a toggle that could disable the lock.
    data["honesty_lock"] = True
    data["honesty_lock_text"] = HONESTY_LOCK
    return data


def save_shop(shop: dict[str, Any]) -> None:
    payload = {
        "name": str(shop.get("name") or "Francabel").strip() or "Francabel",
        "cities": _as_list(shop.get("cities")),
        "desk_hour": str(shop.get("desk_hour") or "3:00").strip() or "3:00",
        "posts_per_night": min(3, max(1, int(shop.get("posts_per_night") or 2))),
        "extra_platforms": _as_list(shop.get("extra_platforms")),
        "extra_services": _as_list(shop.get("extra_services")),
        "facebook_page_token": str(shop.get("facebook_page_token") or "").strip(),
        "linkedin_token": str(shop.get("linkedin_token") or "").strip(),
        "website": str(shop.get("website") or "https://francabel.com").strip() or "https://francabel.com",
        "honesty_lock": True,
    }
    path = shop_path()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")


def all_services(shop: dict[str, Any] | None = None) -> list[str]:
    shop = shop or load_shop()
    seen: list[str] = []
    for name in CORE_SERVICES + list(shop.get("extra_services") or []):
        n = str(name).strip()
        if n and n not in seen:
            seen.append(n)
    return seen


def area_phrase(shop: dict[str, Any]) -> str:
    cities = [c.strip() for c in (shop.get("cities") or []) if str(c).strip()]
    if not cities:
        return "this service area"
    if len(cities) == 1:
        return cities[0]
    if len(cities) == 2:
        return f"{cities[0]} and {cities[1]}"
    return f"{', '.join(cities[:-1])}, and {cities[-1]}"


def crews_line(shop: dict[str, Any]) -> str:
    cities = [c.strip() for c in (shop.get("cities") or []) if str(c).strip()]
    if not cities:
        return "Local crews on call."
    if len(cities) == 1:
        return f"Crews in {cities[0]}."
    if len(cities) == 2:
        return f"Crews in {cities[0]} and {cities[1]}."
    return f"Crews in {', '.join(cities[:-1])}, and {cities[-1]}."
