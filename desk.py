"""Overnight desk: seasonal story, captions, shot lists, queue, packs. Offline. No fake customers."""

from __future__ import annotations

import json
import os
import random
import shutil
import uuid
from datetime import datetime, date
from typing import Any

from paths import export_dir, pack_path, packs_dir, queue_path
from shop import CORE_SERVICES, all_services, area_phrase, crews_line, load_shop
from visuals import visual_for

PLATFORMS = ("facebook", "instagram", "tiktok", "linkedin", "x")

FORMAT_SPECS = {
    "square": {
        "key": "square",
        "label": "1:1 square · 1080×1080 JPEG or PNG · Feed (Instagram, Facebook, LinkedIn)",
        "ratio": "1:1",
        "width": 1080,
        "height": 1080,
        "ext": "jpg",
    },
    "story": {
        "key": "story",
        "label": "9:16 portrait · 1080×1920 JPEG or PNG · Stories, Reels, TikTok",
        "ratio": "9:16",
        "width": 1080,
        "height": 1920,
        "ext": "jpg",
    },
    "landscape": {
        "key": "landscape",
        "label": "16:9 landscape · 1280×720 JPEG or PNG · YouTube, LinkedIn, Facebook video still",
        "ratio": "16:9",
        "width": 1280,
        "height": 720,
        "ext": "jpg",
    },
}

def format_key(label_or_key: str) -> str:
    raw = (label_or_key or "square").strip()
    if raw in FORMAT_SPECS:
        return raw
    for key, spec in FORMAT_SPECS.items():
        if raw == spec["label"] or raw.startswith(spec["ratio"]):
            return key
    low = raw.lower()
    if "9:16" in low or "portrait" in low or "story" in low:
        return "story"
    if "16:9" in low or "landscape" in low or "1280" in low:
        return "landscape"
    return "square"

COMPOSE_URLS = {
    "facebook": "https://www.facebook.com/",
    "instagram": "https://www.instagram.com/",
    "tiktok": "https://www.tiktok.com/tiktokstudio/upload/post/photo",
    "linkedin": "https://www.linkedin.com/feed/",
    "x": "https://x.com/compose/post",
}

COMPOSITE_FOOTER = "Visual: COMPOSITE — generated scene, not a named customer job."

# Catchy hooks + a real question. Never a named family, never a fake completed job.
SERVICE_COPY: dict[str, dict[str, Any]] = {
    "Water heater replacement": {
        "hooks": [
            "Cold water does not wait for a convenient Saturday.",
            "The tank has a birthday. Most people never look.",
            "Heat wave, long showers, a tired anode rod.",
            "When the water goes cold, the clock starts.",
        ],
        "questions": [
            "When was the tank last flushed?",
            "Gas or electric — do you know which unit is in the closet?",
            "Same-day swap, or a planned window this week?",
            "Is the tank leaking, rumbling, or just out of hot water?",
        ],
        "shots": [
            [
                "0–4s: utility closet door, no faces, tank silhouette only",
                "4–8s: close on pipes and drain valve, still, COMPOSITE-safe",
                "8–12s: hold on the on-screen question card",
            ],
            [
                "0–4s: exterior hose bib, late-summer light, no address shown",
                "4–8s: hands-off still of a generic tank jacket (stock/COMPOSITE)",
                "8–12s: cut to the question, then the voice line",
            ],
        ],
        "voices": [
            "If the water went cold, ask about a replacement window. Crews, not a highlight reel.",
            "Flush date unknown is a reason to call. No invented testimonials here.",
        ],
        "fb": [
            "{hook} {crews} This is a service-area note, not a recap of someone else's house. {question}",
            "Overnight desk. {hook} If you are in {area}, the question is practical: {question}",
        ],
        "ig": [
            "{hook}\n{crews}\n{question}",
            "{hook} / {area}\n{question}",
        ],
        "tt": [
            "{hook} {question}",
            "Tank's tired. {question}",
        ],
        "li": [
            "{name}: water heater replacement for homes and small shops in {area}. {crews} {question} We do not publish named-customer claims.",
            "Facility note — {season}. Hot-water equipment fails on its own calendar. {crews} {question}",
        ],
    },
    "Basketball hoop installation": {
        "hooks": [
            "Who's got next?",
            "The driveway is a court if the rim is true.",
            "Back-to-school hours. After-dinner light. A hoop that actually holds.",
            "Portable or in-ground — the yard decides, not a caption.",
        ],
        "questions": [
            "In-ground or portable — what does the yard allow?",
            "Who's got next on your block?",
            "Ten-foot rim, or adjustable for the kid still growing?",
            "Driveway overlay or a true post in the ground?",
        ],
        "shots": [
            [
                "0–4s: empty driveway at dusk, hoop silhouette, no faces",
                "4–8s: net and hardware close, stock/COMPOSITE still",
                "8–12s: hold on the question card",
            ],
            [
                "0–4s: wide yard, late summer, no house numbers",
                "4–8s: backboard edge and rim, no named family, no trophy shot",
                "8–12s: on-screen question, then voice",
            ],
        ],
        "voices": [
            "Who's got next. Ask about the install, not a fake before-and-after of a named family.",
            "Driveway or in-ground. Crews in the service area. Ask.",
        ],
        "fb": [
            "{hook} {crews} Not a story about a family we invented. Just the install question: {question}",
            "Overnight desk for hoop installs in {area}. {hook} {question}",
        ],
        "ig": [
            "{hook}\n{crews}\n{question}",
            "Who's got next.\n{area}\n{question}",
        ],
        "tt": [
            "{hook} {question}",
            "Who's got next. {question}",
        ],
        "li": [
            "{name} installs basketball hoops in {area}. Site constraints (setback, concrete, portable vs in-ground) come first. {question}",
            "Recreation install work — {season}. {crews} {question} No fabricated testimonials.",
        ],
    },
    "Catering / parties": {
        "hooks": [
            "The table is the party.",
            "Labor Day is a long table, not a content recap.",
            "Weekend count: how many plates?",
            "Heat holds. People still gather. The menu is the plan.",
        ],
        "questions": [
            "How many seats this weekend?",
            "Indoor spread or yard table?",
            "Drop-off or full service?",
            "What time should the first tray land?",
        ],
        "shots": [
            [
                "0–4s: empty table setting, no guests, no named hosts",
                "4–8s: serving ware still, COMPOSITE/stock",
                "8–12s: question card over the table",
            ],
            [
                "0–4s: outdoor table, late-summer light, no faces",
                "4–8s: hands-off tray detail",
                "8–12s: hold question, voice line",
            ],
        ],
        "voices": [
            "How many seats. That is the brief. We will not invent a glowing review from a family that does not exist.",
            "The table is the party. Ask for a count.",
        ],
        "fb": [
            "{hook} {crews} If you are planning a gather in {area}, the real question is {question} No fake guest-of-honor captions.",
            "Overnight desk. {season}. {hook} {question}",
        ],
        "ig": [
            "{hook}\n{crews}\n{question}",
            "The table is the party.\n{question}",
        ],
        "tt": [
            "{hook} {question}",
            "How many plates. {question}",
        ],
        "li": [
            "{name} catering / parties — {area}. Event volume, timing, and drop-off vs service. {question} We do not post invented host names.",
            "Hospitality note for {season}. {crews} {question}",
        ],
    },
    "Government contracts": {
        "hooks": [
            "Bid season does not wait for Monday.",
            "Fiscal year turns. Packets either ready or not.",
            "The work is the paperwork, then the work.",
            "Closeout and pursuit share a calendar in September.",
        ],
        "questions": [
            "Is the packet current for this window?",
            "Which codes are you actually bidding?",
            "September: closeout or pursuit?",
            "Who holds the SAM registration, and is it active?",
        ],
        "shots": [
            [
                "0–4s: desk, unmarked folders, no agency logos we do not have rights to",
                "4–8s: calendar page, fiscal-year still",
                "8–12s: question card",
            ],
            [
                "0–4s: columns / civic exterior stock, COMPOSITE-safe, no fake award",
                "4–8s: hands-off paperwork stack",
                "8–12s: hold question and voice",
            ],
        ],
        "voices": [
            "Bid season does not wait. Ask about the packet. No invented award announcements.",
            "Fiscal window. Ready or not. That is the post.",
        ],
        "fb": [
            "{hook} {crews} {name} talks about government-contract support in {area} as a service, not as a trophy wall of fake wins. {question}",
            "Overnight desk. {season}. {hook} {question}",
        ],
        "ig": [
            "{hook}\n{crews}\n{question}",
            "Bid season.\n{question}",
        ],
        "tt": [
            "{hook} {question}",
            "Packet ready? {question}",
        ],
        "li": [
            "{name} — government contracts support in {area}. Capability, current registrations, and the live window. {question} We will not invent named awards.",
            "Public-sector calendar note ({season}). {crews} {question}",
        ],
    },
}

GENERIC_COPY = {
    "hooks": [
        "{service} — when the season asks.",
        "The job has a window. {service} is on the overnight desk.",
        "Not a testimonial. A question about {service}.",
    ],
    "questions": [
        "Need {service_l} on the calendar?",
        "What is the actual constraint on site?",
        "This week, or a planned slot?",
    ],
    "shots": [
        [
            "0–4s: wide, no faces, no house numbers",
            "4–8s: tool or material still, COMPOSITE",
            "8–12s: on-screen question",
        ]
    ],
    "voices": [
        "Ask about {service_l}. This desk will not invent a customer name.",
    ],
    "fb": [
        "{hook} {crews} Service: {service}. {question} No fake named customers.",
    ],
    "ig": [
        "{hook}\n{crews}\n{question}",
    ],
    "tt": [
        "{hook} {question}",
    ],
    "li": [
        "{name} — {service} in {area}. {crews} {question}",
    ],
}

STORY_TEMPLATES = {
    "Labor Day": [
        "{name} overnight desk. Labor Day week is the last unhurried gather of late summer. Heat still sits on the pavement. This is not a recap of named families — it is a shop clock for people in {area}: {services}.",
        "Labor Day is a long weekend, not a testimonial reel. {name} writes tonight for {area}. On the slate: {services}.",
    ],
    "late summer": [
        "Late summer still holds the heat. {name} overnight desk for {area}. Tonight's jobs on paper — not invented customers: {services}.",
        "August-into-September light. Crews in {area}. The desk will not say we just finished a house for a family we made up. On deck: {services}.",
    ],
    "heat": [
        "Heat is a load. Water, shade, after-dark hours. {name} desk, {area}. Story of the day is practical: {services}.",
        "The air has not broken yet. {crews} Tonight's slate: {services}.",
    ],
    "back-to-school": [
        "Back-to-school hours change the driveway and the dinner table. {name} overnight desk, {area}. {services}. No fake parent reviews.",
        "School bells, earlier evenings. The desk asks real questions about {services} in {area}.",
    ],
    "storms": [
        "Storm season is a preparedness note, not a disaster trophy. {name} for {area}. On the desk: {services}.",
        "Watch the Gulf and the Atlantic if that is your map. Then look at the tank, the hoop anchors, the event tent. {crews} {services}.",
    ],
    "fiscal year": [
        "The federal fiscal year turns October 1. September is closeout and pursuit at once. {name} desk — {services} — written for {area}, not as a fake award post.",
        "Fiscal calendars do not care about weekends. {crews} Tonight: {services}.",
    ],
    "weekend parties": [
        "Weekend parties are a headcount, a drop-off time, a table. {name} overnight desk for {area}. {services}.",
        "If the gather is this weekend, the question is seats and timing — not a staged family photo. {crews} {services}.",
    ],
    "bid season": [
        "Bid season does not wait for Monday. {name} writes the night notes for {area}. {services}.",
        "Packets, windows, registrations. {crews} On the desk: {services}. No invented contract wins.",
    ],
}


def labor_day(year: int) -> date:
    d = date(year, 9, 1)
    # First Monday in September
    return date(year, 9, 1 + ((7 - d.weekday()) % 7))


def detect_seasons(when: datetime) -> list[str]:
    seasons: list[str] = []
    ld = labor_day(when.year)
    delta = abs((when.date() - ld).days)
    month, day = when.month, when.day
    if delta <= 6:
        seasons.append("Labor Day")
    if (month, day) >= (8, 10) and (month, day) <= (9, 20):
        seasons.append("late summer")
    if 6 <= month <= 9:
        seasons.append("heat")
    if (month, day) >= (8, 10) and (month, day) <= (9, 15):
        seasons.append("back-to-school")
    if 6 <= month <= 11:
        seasons.append("storms")
    if month in (8, 9) or (month == 10 and day <= 15):
        seasons.append("fiscal year")
        seasons.append("bid season")
    if when.weekday() >= 4 or month in (5, 6, 7, 8, 9):
        seasons.append("weekend parties")
    # de-dupe, keep order
    out: list[str] = []
    for s in seasons:
        if s not in out:
            out.append(s)
    return out or ["late summer"]


def _bank(service: str) -> dict[str, Any]:
    return SERVICE_COPY.get(service, GENERIC_COPY)


def _fill(template: str, ctx: dict[str, str]) -> str:
    try:
        return template.format(**ctx)
    except KeyError:
        return template


def _pick_services(shop: dict[str, Any], rng: random.Random) -> list[str]:
    names = all_services(shop)
    n = min(3, max(1, int(shop.get("posts_per_night") or 2)))
    n = min(n, len(names)) or 1
    if len(names) <= n:
        return list(names)
    # Prefer a mix of core + extra: sample without replacement.
    return rng.sample(names, n)


def write_story(shop: dict[str, Any], seasons: list[str], services: list[str], rng: random.Random) -> tuple[str, str]:
    season = seasons[0]
    bank = STORY_TEMPLATES.get(season) or STORY_TEMPLATES["late summer"]
    ctx = {
        "name": shop.get("name") or "Francabel",
        "area": area_phrase(shop),
        "crews": crews_line(shop),
        "services": ", ".join(services),
        "season": season,
    }
    return season, _fill(rng.choice(bank), ctx)


def make_post(
    shop: dict[str, Any],
    service: str,
    fmt: str,
    season: str,
    story: str,
    when: datetime,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    rng = rng or random.Random()
    bank = _bank(service)
    ctx = {
        "name": shop.get("name") or "Francabel",
        "area": area_phrase(shop),
        "crews": crews_line(shop),
        "season": season,
        "service": service,
        "service_l": service.lower(),
        "hook": "",
        "question": "",
    }
    hook = _fill(rng.choice(bank["hooks"]), ctx)
    question = _fill(rng.choice(bank["questions"]), ctx)
    ctx["hook"] = hook
    ctx["question"] = question
    x_bank = bank.get("x") or bank.get("tt")
    captions = {
        "facebook": _fill(rng.choice(bank["fb"]), ctx),
        "instagram": _fill(rng.choice(bank["ig"]), ctx),
        "tiktok": _fill(rng.choice(bank["tt"]), ctx),
        "linkedin": _fill(rng.choice(bank["li"]), ctx),
        "x": _fill(rng.choice(x_bank), ctx),
    }
    visual, composite = visual_for(service, make_fallback=True)
    footer = COMPOSITE_FOOTER if composite else ""
    if footer:
        for key in captions:
            captions[key] = captions[key].rstrip() + "\n\n" + footer
    shots = rng.choice(bank["shots"])
    voice = _fill(rng.choice(bank["voices"]), ctx)
    post_id = uuid.uuid4().hex[:12]
    spec = FORMAT_SPECS.get(format_key(fmt)) or FORMAT_SPECS["square"]
    fmt_key = spec["key"]
    return {
        "id": post_id,
        "created_at": when.isoformat(timespec="seconds"),
        "date": when.strftime("%Y-%m-%d"),
        "service": service,
        "format": fmt_key,
        "format_label": spec["label"],
        "width": spec["width"],
        "height": spec["height"],
        "ratio": spec["ratio"],
        "file_kind": "JPEG or PNG",
        "hook": hook,
        "question": question,
        "story": story,
        "season": season,
        "captions": captions,
        "shot_list": {
            "duration_sec": 12,
            "shots": list(shots),
            "on_screen_question": question,
            "voice_line": voice,
        },
        "visual": visual,
        "visual_label": "COMPOSITE" if composite else None,
        "visual_footer": footer or None,
        "status": "queued",
        "platforms": list(PLATFORMS),
    }


def generate_pack(shop: dict[str, Any] | None = None, when: datetime | None = None) -> dict[str, Any]:
    shop = shop or load_shop()
    when = when or datetime.now()
    rng = random.Random(when.strftime("%Y-%m-%d") + uuid.uuid4().hex[:8])
    seasons = detect_seasons(when)
    services = _pick_services(shop, rng)
    season, story = write_story(shop, seasons, services, rng)
    posts = []
    for i, svc in enumerate(services):
        fmt = "story" if i % 2 else "square"
        posts.append(make_post(shop, svc, fmt, season, story, when, rng))
    return {
        "date": when.strftime("%Y-%m-%d"),
        "generated_at": when.isoformat(timespec="seconds"),
        "shop_name": shop.get("name") or "Francabel",
        "season": season,
        "seasons": seasons,
        "story_of_the_day": story,
        "posts": posts,
        "honesty": (
            "No named customers, families, or testimonials were invented. "
            "Cities are service area only. Generated visuals are labeled COMPOSITE."
        ),
    }


def save_pack(pack: dict[str, Any]) -> str:
    path = pack_path(pack["date"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)
        fh.write("\n")
    return path


def load_pack(day: str) -> dict[str, Any] | None:
    path = pack_path(day)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def latest_pack() -> dict[str, Any] | None:
    today = datetime.now().strftime("%Y-%m-%d")
    pack = load_pack(today)
    if pack:
        return pack
    try:
        names = sorted(os.listdir(packs_dir()), reverse=True)
    except OSError:
        return None
    for name in names:
        if name.endswith(".json"):
            return load_pack(name[:-5])
    return None


def load_queue() -> list[dict[str, Any]]:
    path = queue_path()
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return [p for p in data if isinstance(p, dict)]
        if isinstance(data, dict) and isinstance(data.get("posts"), list):
            return [p for p in data["posts"] if isinstance(p, dict)]
    except (OSError, json.JSONDecodeError):
        pass
    return []


def save_queue(queue: list[dict[str, Any]]) -> None:
    path = queue_path()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(queue, fh, indent=2)
        fh.write("\n")


def add_to_queue(post: dict[str, Any]) -> None:
    queue = load_queue()
    queue.append(post)
    save_queue(queue)


def set_status(post_id: str, status: str) -> dict[str, Any] | None:
    if status not in ("queued", "exported", "posted"):
        return None
    queue = load_queue()
    found = None
    for post in queue:
        if post.get("id") == post_id:
            post["status"] = status
            found = post
            break
    save_queue(queue)
    return found


def find_post(post_id: str) -> dict[str, Any] | None:
    for post in load_queue():
        if post.get("id") == post_id:
            return post
    return None


def save_post(updated: dict[str, Any]) -> None:
    queue = load_queue()
    for i, post in enumerate(queue):
        if post.get("id") == updated.get("id"):
            queue[i] = updated
            save_queue(queue)
            return
    queue.append(updated)
    save_queue(queue)


def import_pack_file(path: str) -> tuple[int, str]:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        return 0, f"Could not read pack: {exc}"
    posts: list[dict[str, Any]] = []
    if isinstance(data, list):
        posts = [p for p in data if isinstance(p, dict)]
    elif isinstance(data, dict):
        if isinstance(data.get("posts"), list):
            posts = [p for p in data["posts"] if isinstance(p, dict)]
        elif data.get("captions") or data.get("service"):
            posts = [data]
    if not posts:
        return 0, "No posts found in that JSON."
    queue = load_queue()
    existing = {p.get("id") for p in queue}
    added = 0
    for post in posts:
        if not post.get("id") or post.get("id") in existing:
            post["id"] = uuid.uuid4().hex[:12]
        post.setdefault("status", "queued")
        post.setdefault("captions", {})
        queue.append(post)
        existing.add(post["id"])
        added += 1
    save_queue(queue)
    return added, f"Imported {added} post(s) into the queue."


def export_post(post: dict[str, Any]) -> str:
    folder = os.path.join(export_dir(), str(post.get("id") or uuid.uuid4().hex[:8]))
    os.makedirs(folder, exist_ok=True)
    caps = post.get("captions") or {}
    lines = [
        f"Francabel export — {post.get('service')}",
        f"Status: {post.get('status')}",
        f"Format: {post.get('format')}",
        f"Hook: {post.get('hook')}",
        f"Question: {post.get('question')}",
        "",
    ]
    if post.get("visual_label") == "COMPOSITE" or post.get("visual_footer"):
        lines.append(COMPOSITE_FOOTER)
        lines.append("")
    for plat in PLATFORMS:
        lines.append(f"=== {plat.upper()} ===")
        lines.append(caps.get(plat) or "")
        lines.append("")
    shots = post.get("shot_list") or {}
    lines.append("=== 12-SECOND SHOT LIST ===")
    for s in shots.get("shots") or []:
        lines.append(f"- {s}")
    lines.append(f"On-screen question: {shots.get('on_screen_question') or post.get('question')}")
    lines.append(f"Voice: {shots.get('voice_line') or ''}")
    caption_path = os.path.join(folder, "captions.txt")
    with open(caption_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    visual = post.get("visual")
    if visual and os.path.isfile(visual):
        ext = os.path.splitext(visual)[1] or ".png"
        shutil.copy2(visual, os.path.join(folder, f"visual{ext}"))
    with open(os.path.join(folder, "post.json"), "w", encoding="utf-8") as fh:
        json.dump(post, fh, indent=2)
        fh.write("\n")
    return folder


def run_desk(shop: dict[str, Any] | None = None) -> str:
    """CLI / scheduler: write today's pack, append posts to the queue, no GUI."""
    shop = shop or load_shop()
    pack = generate_pack(shop)
    path = save_pack(pack)
    queue = load_queue()
    queue.extend(pack["posts"])
    save_queue(queue)
    return path


def compose_from_template(shop: dict[str, Any], service: str, fmt: str = "square") -> dict[str, Any]:
    when = datetime.now()
    seasons = detect_seasons(when)
    rng = random.Random()
    season, story = write_story(shop, seasons, [service], rng)
    return make_post(shop, service, format_key(fmt), season, story, when, rng)
