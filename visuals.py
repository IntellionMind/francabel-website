"""Match stock posters. Never overwrite hoop/tank/table/columns. Fallback COMPOSITE PNG uses stdlib only."""

from __future__ import annotations

import os
import struct
import zlib

from paths import assets_dir, generated_dir

STOCK = {
    "hoop.png": ("basketball", "hoop", "rim", "backboard", "court"),
    "tank.png": ("water", "heater", "tank", "boiler", "anode"),
    "table.png": ("cater", "party", "parties", "table", "banquet", "event", "food"),
    "columns.png": ("government", "contract", "bid", "federal", "municipal", "procurement", "naics"),
}

PROTECTED_ASSETS = frozenset(STOCK.keys())


def match_visual(service: str) -> str | None:
    """Return an existing assets/*.png path for this service, or None."""
    s = (service or "").lower()
    folder = assets_dir()
    for filename, keys in STOCK.items():
        path = os.path.join(folder, filename)
        if not os.path.isfile(path):
            continue
        if any(key in s for key in keys):
            return path
    return None


def visual_for(service: str, make_fallback: bool = True) -> tuple[str | None, bool]:
    """(path, is_composite). Stock posters are not labeled COMPOSITE; drawn fallbacks are."""
    stock = match_visual(service)
    if stock:
        return stock, False
    if not make_fallback:
        return None, False
    path = draw_composite_poster(service)
    return path, True


def draw_composite_poster(service: str) -> str:
    """Ink-poster PNG for extra services. Written under data/generated/, never into assets/."""
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in service).strip("-") or "service"
    while "--" in slug:
        slug = slug.replace("--", "-")
    out = os.path.join(generated_dir(), f"{slug}.png")
    title = (service or "SERVICE").upper()
    w, h = 800, 800
    bg, rust, cream, brass = (22, 20, 16), (196, 92, 50), (232, 220, 200), (201, 166, 107)
    img = _canvas(w, h, bg)
    _rect(img, w, 0, 0, w, 18, rust)
    _rect(img, w, 0, h - 18, w, 18, rust)
    _rect(img, w, 40, 40, w - 80, h - 80, (31, 26, 21))
    _rect(img, w, 40, 40, w - 80, 8, brass)
    _text(img, w, 64, 80, "FRANCABEL", brass, 3)
    _text(img, w, 64, 130, "OVERNIGHT DESK", cream, 2)
    y = 220
    for line in _wrap(title, 16):
        _text(img, w, 64, y, line, cream, 4)
        y += 48
    _rect(img, w, 64, h - 180, 220, 44, rust)
    _text(img, w, 76, h - 168, "COMPOSITE", cream, 3)
    _text(img, w, 64, h - 110, "NOT A NAMED CUSTOMER JOB", cream, 2)
    _write_png(out, w, h, img)
    return out


# --- tiny RGB canvas + 5x7 font (stdlib PNG) ---

_FONT = {
    " ": [0, 0, 0, 0, 0, 0, 0],
    "A": [14, 17, 17, 31, 17, 17, 17],
    "B": [30, 17, 17, 30, 17, 17, 30],
    "C": [14, 17, 16, 16, 16, 17, 14],
    "D": [30, 17, 17, 17, 17, 17, 30],
    "E": [31, 16, 16, 30, 16, 16, 31],
    "F": [31, 16, 16, 30, 16, 16, 16],
    "G": [14, 17, 16, 19, 17, 17, 14],
    "H": [17, 17, 17, 31, 17, 17, 17],
    "I": [14, 4, 4, 4, 4, 4, 14],
    "J": [1, 1, 1, 1, 17, 17, 14],
    "K": [17, 18, 20, 24, 20, 18, 17],
    "L": [16, 16, 16, 16, 16, 16, 31],
    "M": [17, 27, 21, 21, 17, 17, 17],
    "N": [17, 25, 21, 19, 17, 17, 17],
    "O": [14, 17, 17, 17, 17, 17, 14],
    "P": [30, 17, 17, 30, 16, 16, 16],
    "Q": [14, 17, 17, 17, 21, 18, 13],
    "R": [30, 17, 17, 30, 20, 18, 17],
    "S": [14, 17, 16, 14, 1, 17, 14],
    "T": [31, 4, 4, 4, 4, 4, 4],
    "U": [17, 17, 17, 17, 17, 17, 14],
    "V": [17, 17, 17, 17, 17, 10, 4],
    "W": [17, 17, 17, 21, 21, 21, 10],
    "X": [17, 17, 10, 4, 10, 17, 17],
    "Y": [17, 17, 10, 4, 4, 4, 4],
    "Z": [31, 1, 2, 4, 8, 16, 31],
    "0": [14, 17, 19, 21, 25, 17, 14],
    "1": [4, 12, 4, 4, 4, 4, 14],
    "2": [14, 17, 1, 6, 8, 16, 31],
    "3": [14, 17, 1, 6, 1, 17, 14],
    "4": [2, 6, 10, 18, 31, 2, 2],
    "5": [31, 16, 30, 1, 1, 17, 14],
    "6": [14, 16, 16, 30, 17, 17, 14],
    "7": [31, 1, 2, 4, 8, 8, 8],
    "8": [14, 17, 17, 14, 17, 17, 14],
    "9": [14, 17, 17, 15, 1, 1, 14],
    "-": [0, 0, 0, 14, 0, 0, 0],
    "/": [1, 2, 2, 4, 8, 8, 16],
    "?": [14, 17, 1, 2, 4, 0, 4],
    ".": [0, 0, 0, 0, 0, 0, 4],
    "&": [10, 17, 10, 12, 21, 18, 13],
    "'": [4, 4, 4, 0, 0, 0, 0],
    ":": [0, 4, 0, 0, 0, 4, 0],
}


def _canvas(w: int, h: int, color: tuple[int, int, int]) -> bytearray:
    r, g, b = color
    buf = bytearray(w * h * 3)
    for i in range(0, len(buf), 3):
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b
    return buf


def _rect(img: bytearray, w: int, x: int, y: int, rw: int, rh: int, color: tuple[int, int, int]) -> None:
    h = len(img) // (w * 3)
    r, g, b = color
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(w, x + rw), min(h, y + rh)
    for yy in range(y0, y1):
        row = yy * w * 3
        for xx in range(x0, x1):
            i = row + xx * 3
            img[i] = r
            img[i + 1] = g
            img[i + 2] = b


def _text(img: bytearray, w: int, x: int, y: int, text: str, color: tuple[int, int, int], scale: int) -> None:
    cx = x
    for ch in text.upper():
        glyph = _FONT.get(ch, _FONT["?"])
        for gy, bits in enumerate(glyph):
            for gx in range(5):
                if bits & (1 << (4 - gx)):
                    _rect(img, w, cx + gx * scale, y + gy * scale, scale, scale, color)
        cx += 6 * scale


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [text]


def _write_png(path: str, w: int, h: int, rgb: bytearray) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw.extend(rgb[y * stride : (y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(png)


def load_thumbnail(tk_module, path: str, max_side: int = 160):
    """Return a tk.PhotoImage subsampled to about max_side, or None."""
    if not path or not os.path.isfile(path):
        return None
    try:
        img = tk_module.PhotoImage(file=path)
    except Exception:
        return None
    w, h = img.width(), img.height()
    if w <= 0 or h <= 0:
        return None
    factor = max(1, max(w, h) // max_side)
    if factor > 1:
        try:
            img = img.subsample(factor, factor)
        except Exception:
            pass
    return img
