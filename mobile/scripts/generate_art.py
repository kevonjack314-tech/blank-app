"""Generate the Tiny Steps app art: icon, Android adaptive icon, splash,
and Android notification icon. Run from the mobile/ directory:

    python3 scripts/generate_art.py

The mark is a sprout growing from the top of three ascending steps.
Everything is drawn at 4x and downscaled for smooth edges.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SS = 4  # supersampling factor

GREEN_DARK = (30, 87, 55)
GREEN_MAIN = (46, 125, 79)
GREEN_MID = (53, 145, 90)
GREEN_LEAF = (67, 160, 107)
MINT = (234, 250, 240)
BG_LIGHT = (244, 247, 244)
INK = (28, 43, 33)


def rr(draw, box, radius, fill, corners=None):
    draw.rounded_rectangle(box, radius=radius, fill=fill, corners=corners)


def leaf_points(anchor, length, width, angle_deg, n=48):
    """Pointed leaf polygon: grows from `anchor` along `angle_deg`."""
    a = math.radians(angle_deg)
    cos_a, sin_a = math.cos(a), math.sin(a)
    pts = []
    for side in (1, -1):
        rng = range(n + 1) if side == 1 else range(n, -1, -1)
        for i in rng:
            t = i / n
            x, y = t * length, side * math.sin(math.pi * t) * width / 2
            pts.append((anchor[0] + x * cos_a - y * sin_a, anchor[1] + x * sin_a + y * cos_a))
    return pts


def draw_stem(draw, base, top, thickness, color, bend=0.12, n=60):
    """Slightly curved stem drawn as overlapping circles (round caps)."""
    cx = (base[0] + top[0]) / 2 - bend * abs(base[1] - top[1])
    cy = (base[1] + top[1]) / 2
    r = thickness / 2
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * base[0] + 2 * (1 - t) * t * cx + t**2 * top[0]
        y = (1 - t) ** 2 * base[1] + 2 * (1 - t) * t * cy + t**2 * top[1]
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)


def draw_mark(draw, size, steps_color, sprout_color, offset=(0, 0)):
    """The Tiny Steps mark inside a `size`-px square at `offset`."""
    s = size
    ox, oy = offset

    def B(x0, y0, x1, y1):
        return [ox + x0 * s, oy + y0 * s, ox + x1 * s, oy + y1 * s]

    # Only the outer bottom corners stay rounded so the base is one clean line.
    radius = 0.035 * s
    rr(draw, B(0.10, 0.640, 0.400, 0.880), radius, steps_color, corners=(True, True, False, True))
    rr(draw, B(0.355, 0.515, 0.655, 0.880), radius, steps_color, corners=(True, True, False, False))
    rr(draw, B(0.610, 0.390, 0.910, 0.880), radius, steps_color, corners=(True, True, True, False))

    stem_base = (ox + 0.760 * s, oy + 0.400 * s)
    stem_top = (ox + 0.740 * s, oy + 0.185 * s)
    draw_stem(draw, stem_base, stem_top, 0.030 * s, sprout_color)
    draw.polygon(leaf_points(stem_top, 0.230 * s, 0.130 * s, -160), fill=sprout_color)
    draw.polygon(leaf_points(stem_top, 0.190 * s, 0.110 * s, -55), fill=sprout_color)


def vertical_gradient(size, top_color, bottom_color):
    img = Image.new("RGB", (size, size))
    for y in range(size):
        t = y / (size - 1)
        img.paste(
            tuple(round(a + (b - a) * t) for a, b in zip(top_color, bottom_color)),
            [0, y, size, y + 1],
        )
    return img


def make_icon():
    s = 1024 * SS
    img = vertical_gradient(s, GREEN_MID, GREEN_DARK).convert("RGBA")
    draw = ImageDraw.Draw(img)
    m = 0.10 * s  # inner margin
    draw_mark(draw, s - 2 * m, MINT, (201, 242, 217), offset=(m, m * 0.9))
    img.resize((1024, 1024), Image.LANCZOS).convert("RGB").save(ASSETS / "icon.png")


def make_adaptive_icon():
    # Foreground layer: transparent, mark inside the ~66% safe zone.
    s = 1024 * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    inner = 0.56 * s
    m = (s - inner) / 2
    draw_mark(draw, inner, MINT + (255,), (201, 242, 217, 255), offset=(m, m))
    img.resize((1024, 1024), Image.LANCZOS).save(ASSETS / "adaptive-icon.png")


def make_splash():
    s = 2048 * SS
    img = Image.new("RGB", (s, s), BG_LIGHT)
    draw = ImageDraw.Draw(img)
    mark = 0.34 * s
    draw_mark(draw, mark, GREEN_MAIN, GREEN_LEAF, offset=((s - mark) / 2, 0.26 * s))
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(0.070 * s))
    sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(0.026 * s))
    for text, fnt, color, y in (
        ("Tiny Steps", font, INK, 0.655 * s),
        ("one baby step a day", sub_font, GREEN_MAIN, 0.745 * s),
    ):
        w = draw.textlength(text, font=fnt)
        draw.text(((s - w) / 2, y), text, font=fnt, fill=color)
    img.resize((2048, 2048), Image.LANCZOS).save(ASSETS / "splash.png")


def make_notification_icon():
    # Android status-bar icon: white silhouette on transparency.
    s = 96 * SS * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    white = (255, 255, 255, 255)
    stem_base = (0.50 * s, 0.92 * s)
    stem_top = (0.46 * s, 0.38 * s)
    draw_stem(draw, stem_base, stem_top, 0.13 * s, white, bend=0.10)
    draw.polygon(leaf_points(stem_top, 0.50 * s, 0.30 * s, -160), fill=white)
    draw.polygon(leaf_points(stem_top, 0.42 * s, 0.26 * s, -55), fill=white)
    img.resize((96, 96), Image.LANCZOS).save(ASSETS / "notification-icon.png")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    make_icon()
    make_adaptive_icon()
    make_splash()
    make_notification_icon()
    print("wrote", ", ".join(p.name for p in sorted(ASSETS.glob("*.png"))))
