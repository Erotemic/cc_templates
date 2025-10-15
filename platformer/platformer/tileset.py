# Create a novel pixel-art style spritesheet + tileset and a JSON metadata file
# that maps animation names to frame rects. We'll keep it simple and readable,
# sized for a 48x48 tile-based platformer. No copyrighted characters; our
# character is "ByteBuddy", a floating neon-mask robot slime with small hover
# thrusters. Frames are stylized but simple enough to edit in class.
"""
Fixme: this has import time side effects
"""
from PIL import Image, ImageDraw
import json
from math import sin, pi
import ubelt as ub

cache_dpath = ub.Path.appdir("platformer").ensuredir()

# TODO: Use data from: blob:https://imgur.com/8c5587db-38ee-4ca5-b28b-42aa474a498e

meta_path = cache_dpath / "bytebuddy_meta.json"
tileset_path = cache_dpath / "bytebuddy_tileset.png"
sheet_path = cache_dpath / "bytebuddy_spritesheet.png"

TILE = 48
SCALE = 1  # keep 1:1 pixels for now (teachers can upscale later if desired)

# Animation plan
ANIMS = {
    "idle": 4,
    "run": 6,
    "jump": 2,
    "fall": 2,
    "attack": 4,
    "hurt": 1,
}

# Layout parameters
PADDING = 2  # gap between frames
COLS = 8  # frames per row before wrapping
BG = (0, 0, 0, 0)  # transparent

# Color palette (friendly neon)
C = {
    "body": (50, 200, 240, 255),  # cyan body
    "outline": (20, 60, 80, 255),
    "visor": (255, 255, 255, 255),  # white LED visor
    "visor_glow": (120, 230, 255, 140),
    "accent": (255, 90, 150, 255),  # magenta accent
    "thruster": (255, 200, 50, 255),  # orange flame
    "shadow": (0, 0, 0, 60),
    "saber": (120, 255, 140, 255),  # attack swipe
}


def new_canvas(cols, rows):
    w = cols * TILE + (cols + 1) * PADDING
    h = rows * TILE + (rows + 1) * PADDING
    img = Image.new("RGBA", (w, h), BG)
    return img


def place_rect(row, col):
    x = PADDING + col * (TILE + PADDING)
    y = PADDING + row * (TILE + PADDING)
    return (x, y, x + TILE, y + TILE)


def draw_bytebuddy(draw: ImageDraw.ImageDraw, box, phase=0.0, action="idle"):
    # Draw a round-corner body slime with an LED visor and small side fins.
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2

    # Hover offset for liveliness
    hover = int(2 * sin(phase * 2 * pi))
    y0h = y0 + hover
    y1h = y1 + hover

    # Body
    body_rect = [x0 + 6, y0h + 10, x1 - 6, y1h - 6]
    draw.rounded_rectangle(
        body_rect, radius=14, fill=C["body"], outline=C["outline"], width=2
    )

    # Fins (left/right) - wiggle on run
    fin_y = (body_rect[1] + body_rect[3]) // 2
    wiggle = int(4 * sin(phase * 2 * pi)) if action in ("run", "attack") else 0
    # Left fin
    draw.polygon(
        [
            (body_rect[0] - 6, fin_y - 6 + wiggle),
            (body_rect[0] + 2, fin_y),
            (body_rect[0] - 6, fin_y + 6 - wiggle),
        ],
        fill=C["accent"],
    )
    # Right fin
    draw.polygon(
        [
            (body_rect[2] + 6, fin_y - 6 - wiggle),
            (body_rect[2] - 2, fin_y),
            (body_rect[2] + 6, fin_y + 6 + wiggle),
        ],
        fill=C["accent"],
    )

    # Visor area
    visor_rect = [cx - 10, y0h + 16, cx + 10, y0h + 24]
    draw.rounded_rectangle(
        visor_rect, radius=4, fill=C["visor"], outline=C["outline"], width=1
    )
    # Visor eyes (vary by action)
    if action == "hurt":
        # X_X
        draw.line(
            (
                visor_rect[0] + 2,
                visor_rect[1] + 1,
                visor_rect[0] + 8,
                visor_rect[1] + 7,
            ),
            fill=C["outline"],
            width=2,
        )
        draw.line(
            (
                visor_rect[0] + 8,
                visor_rect[1] + 1,
                visor_rect[0] + 2,
                visor_rect[1] + 7,
            ),
            fill=C["outline"],
            width=2,
        )
        draw.line(
            (
                visor_rect[2] - 8,
                visor_rect[1] + 1,
                visor_rect[2] - 2,
                visor_rect[1] + 7,
            ),
            fill=C["outline"],
            width=2,
        )
        draw.line(
            (
                visor_rect[2] - 2,
                visor_rect[1] + 1,
                visor_rect[2] - 8,
                visor_rect[1] + 7,
            ),
            fill=C["outline"],
            width=2,
        )
    else:
        # friendly pixels
        draw.rectangle(
            [
                visor_rect[0] + 3,
                visor_rect[1] + 3,
                visor_rect[0] + 6,
                visor_rect[1] + 6,
            ],
            fill=C["outline"],
        )
        draw.rectangle(
            [
                visor_rect[2] - 6,
                visor_rect[1] + 3,
                visor_rect[2] - 3,
                visor_rect[1] + 6,
            ],
            fill=C["outline"],
        )

    # Thruster flames on jump/fall
    if action in ("jump", "fall"):
        flame_y = body_rect[3] + 1
        for dx in (-6, 6):
            draw.polygon(
                [
                    (cx + dx - 3, flame_y),
                    (cx + dx + 3, flame_y),
                    (cx + dx, flame_y + 8 + (2 if action == "fall" else 0)),
                ],
                fill=C["thruster"],
            )

    # Attack swipe / sparkle
    if action == "attack":
        # a quick saber arc in front
        arc_box = [cx - 4, y0h + 6, cx + 30, y0h + 30]
        draw.arc(arc_box, start=300, end=30, fill=C["saber"], width=3)

    # Simple shadow on ground for grounding
    draw.ellipse([cx - 10, y1 - 8, cx + 10, y1 - 4], fill=C["shadow"])


def build_character_sheet():
    total_frames = sum(ANIMS.values())
    rows = (total_frames + COLS - 1) // COLS
    sheet = new_canvas(cols=COLS, rows=rows)
    draw = ImageDraw.Draw(sheet)

    meta = {"tile": TILE, "anims": {}, "frames": {}}

    r = c = 0
    frame_index = 0
    for anim_name, count in ANIMS.items():
        meta["anims"][anim_name] = {"start": frame_index, "count": count}
        for i in range(count):
            box = place_rect(r, c)
            phase = i / max(count, 1)
            draw_bytebuddy(draw, box, phase=phase, action=anim_name)
            meta["frames"][str(frame_index)] = {
                "x": box[0],
                "y": box[1],
                "w": TILE,
                "h": TILE,
            }

            frame_index += 1
            c += 1
            if c >= COLS:
                c = 0
                r += 1

    sheet.save(sheet_path, "PNG")

    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    return sheet_path, meta_path, sheet_size, meta


def build_tileset():
    # A tiny tileset: grass, dirt, stone, platform metal, spike, coin, heart
    tiles_across = 8
    rows = 2
    img = new_canvas(tiles_across, rows)
    d = ImageDraw.Draw(img)

    def tile_box(r, c):
        x = PADDING + c * (TILE + PADDING)
        y = PADDING + r * (TILE + PADDING)
        return (x, y, x + TILE, y + TILE)

    # Row 0: terrain
    # Grass
    b = tile_box(0, 0)
    d.rectangle([b[0], b[1] + 10, b[2], b[3]], fill=(120, 80, 40, 255))  # dirt
    d.rectangle([b[0], b[1] + 4, b[2], b[1] + 14], fill=(90, 200, 90, 255))  # grass cap
    # Dirt
    b = tile_box(0, 1)
    d.rectangle([b[0], b[1], b[2], b[3]], fill=(140, 100, 60, 255))
    # Stone
    b = tile_box(0, 2)
    d.rectangle([b[0], b[1], b[2], b[3]], fill=(110, 120, 130, 255))
    # Metal platform
    b = tile_box(0, 3)
    d.rectangle(
        [b[0], b[1] + 6, b[2], b[3] - 6],
        fill=(60, 80, 110, 255),
        outline=(20, 30, 50, 255),
        width=2,
    )

    # Spikes
    b = tile_box(0, 4)
    for i in range(0, TILE, 12):
        d.polygon(
            [(b[0] + i, b[3]), (b[0] + i + 6, b[1] + 10), (b[0] + i + 12, b[3])],
            fill=(230, 230, 240, 255),
            outline=(70, 70, 90, 255),
        )

    # Row 1: collectibles & UI
    # Coin
    b = tile_box(1, 0)
    d.ellipse(
        [b[0] + 8, b[1] + 8, b[2] - 8, b[3] - 8],
        fill=(255, 220, 80, 255),
        outline=(160, 130, 40, 255),
        width=2,
    )
    # Gem
    b = tile_box(1, 1)
    d.polygon(
        [
            (b[0] + TILE // 2, b[1] + 6),
            (b[2] - 8, b[1] + TILE // 2),
            (b[0] + TILE // 2, b[3] - 6),
            (b[0] + 8, b[1] + TILE // 2),
        ],
        fill=(120, 230, 255, 255),
        outline=(40, 100, 130, 255),
        width=2,
    )
    # Heart
    b = tile_box(1, 2)
    d.polygon(
        [
            (b[0] + 8, b[1] + 18),
            (b[0] + TILE // 2, b[3] - 10),
            (b[2] - 8, b[1] + 18),
            (b[2] - 14, b[1] + 8),
            (b[0] + TILE // 2, b[1] + 14),
            (b[0] + 14, b[1] + 8),
        ],
        fill=(255, 90, 120, 255),
        outline=(160, 40, 70, 255),
        width=2,
    )
    # Key
    b = tile_box(1, 3)
    d.ellipse(
        [b[0] + 8, b[1] + 8, b[0] + 24, b[1] + 24], outline=(200, 180, 80, 255), width=3
    )
    d.rectangle([b[0] + 24, b[1] + 16, b[2] - 8, b[1] + 20], fill=(200, 180, 80, 255))

    # Debug colored squares
    colors = [
        (80, 160, 255, 255),
        (120, 220, 120, 255),
        (230, 120, 120, 255),
        (200, 200, 80, 255),
    ]
    for i, col in enumerate(colors):
        b = tile_box(1, 4 + i)
        d.rectangle([b[0], b[1], b[2], b[3]], fill=col)

    # path = "/mnt/data/bytebuddy_tileset.png"
    img.save(tileset_path, "PNG")
    return tileset_path, img.size


sheet_path, meta_path, sheet_size, meta = build_character_sheet()
tiles_path, tiles_size = build_tileset()

# def build_tileset():
#     # sheet_path, meta_path, tiles_path, sheet_size, tiles_size, meta


# if __name__ == '__main__':
#     build_tileset()
