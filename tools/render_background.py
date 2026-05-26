"""Render the static background for The Great Farm Crossing UI.

One-shot deterministic compositor. Every tile/sprite is placed at a HARDCODED
coordinate below; there is zero randomness. If the result looks ugly, edit
the coordinates and re-run.

Outputs:
  assets/ui/background_spring_1024x600.png  (final 1024x600 PNG)
  assets/ui/background_preview.png          (50% scale preview)

Optional:
  python tools/render_background.py --contact-sheet
    Dumps numbered grids of the tile-grid sheets used by Pass 1/2 so the
    coordinate tables below can be reviewed.

Layout (tile size = 32 px, grid = 32 cols x 19 rows):
  - Cols 0..8   : left grass margin       (288 px wide)
  - Col  9      : LEFT BANK  (rocks)
  - Cols 10..21 : flowing water interior  (12 tiles wide = 384 px)
  - Col  22     : RIGHT BANK (rocks)
  - Cols 23..31 : right grass margin

The river is wider than the bare minimum so that the boat sprite (~125 px),
anchored at LEFT_DOCK_X=336 (pixel center, col 10.5) and RIGHT_DOCK_X=688
(col 21.5), is comfortably over water on both sides of the crossing. With
banks at cols 9 and 22, the boat at the left dock spans cols 8.5..12.4 which
is mostly water (cols 10..12); same on the right dock.

UI constants (from ui/constants.py, NOT modified):
  LEFT_DOCK_X  = 336   RIGHT_DOCK_X = 688   BOAT_Y = 288 (row 9)

HUD covers y in [0, 48) and y in [560, 600). Queue zones occupy x in
[120, 280] and [800, 960] with y in [80, 500] roughly. The water lane the
boat traverses is cols 10..21, rows 8..10 (kept empty).

Decoration sources:
  Tile-grid sheets (32x32):
    vectoraith/.../terrain_spring_expanded_32x32.png      grass + river
    vectoraith/.../details_spring_32x32.png (Modular)     flowers, tufts, planks
  Standalone sprite PNGs (pre-cropped, NOT on a 32x32 grid; pasted at
  hardcoded pixel positions at native size):
    vectoraith/.../Tilesets (Compact)/house.png   small farmhouse (scaled)
    vectoraith/.../Tilesets (Compact)/tree.png    full tree
    vectoraith/.../Tilesets (Compact)/corn.png    corn stalk
    vectoraith/.../Tilesets (Compact)/fences.png  3-post fence strip
    vectoraith/.../Tilesets (Compact)/dirt.png    dirt patch

Tradeoffs / notes:
  - The spring tileset has no plain water tile; the WATERFALL block at
    cols 0-2 rows 11-13 is reused. Tile (1,12) tiles cleanly top-to-bottom
    with a downward-flow look that reads as a river.
  - The "dock" is built from modular log tiles (1..3, 2) used as planks.
  - The house is large (162x184). Even scaled to 80% it overlaps a strip of
    the left queue zone near the very bottom (y > 470). Queue sprites stack
    from the top of that zone so this tail end is empty in practice — we
    accept the small overlap to keep the requested house visible.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[1]
TS_COMPACT = REPO / "assets" / "vectoraith" / "32x32" / "Tilesets (Compact)"
TS_MODULAR = REPO / "assets" / "vectoraith" / "32x32" / "Tilesets (Modular)"
OUT_DIR = REPO / "assets" / "ui"

TILE = 32
W, H = 1024, 600
COLS = W // TILE                      # 32
ROWS = (H + TILE - 1) // TILE         # 19

# ---- Source sheets (tile-grid) ----------------------------------------------
SPRING_PNG  = TS_COMPACT / "vectoraith_tileset_farmingsims_terrain_spring_expanded_32x32.png"
DETAILS_PNG = TS_MODULAR / "vectoraith_tileset_farmingsims_details_spring_32x32.png"

# ---- Standalone sprite PNGs (pre-cropped) -----------------------------------
HOUSE_PNG = TS_COMPACT / "house.png"
TREE_PNG  = TS_COMPACT / "tree.png"
CORN_PNG  = TS_COMPACT / "corn.png"
FENCE_PNG = TS_COMPACT / "fences.png"
DIRT_PNG  = TS_COMPACT / "dirt.png"

# ---- Tile coordinates (col, row) in the source sheets -----------------------
GRASS_PLAIN  = (1, 0)
GRASS_VAR1   = (2, 0)

# Waterfall block at cols 0..2 rows 11..13 of spring sheet.
LBANK_TILE   = (0, 12)
WATER_TILE   = (1, 12)
RBANK_TILE   = (2, 12)

# Modular details sheet small overlays.
LOG_LEFT   = (1, 2)
LOG_MID    = (2, 2)
LOG_RIGHT  = (3, 2)
FLOWER_YEL = (0, 5)
FLOWER_WHT = (0, 6)
FLOWER_BLU = (0, 8)
TUFT_A     = (8, 1)
TUFT_B     = (10, 1)
TUFT_C     = (8, 3)

# ---- River geometry ----------------------------------------------------------
LBANK_COL = 9
RBANK_COL = 22
WATER_COLS = range(LBANK_COL + 1, RBANK_COL)

# Pier sits on the bank tile and extends one tile into the water at row 9.
LEFT_PIER_COLS  = (LBANK_COL, LBANK_COL + 1)   # cols 9, 10
RIGHT_PIER_COLS = (RBANK_COL - 1, RBANK_COL)   # cols 21, 22
PIER_ROW = 9

# ---- Small tile-grid decorations on grass margins ---------------------------
# (output_col, output_row, sheet_key, (source_col, source_row))
# Safe LEFT grass cols (outside queue cols 3.75..8.75): 0, 1, 2, 3.
# Safe RIGHT grass cols (outside queue cols 25..30):   23, 24, 31.
TILE_DECOS: list[tuple[int, int, str, tuple[int, int]]] = [
    # Left margin grass variants.
    (0, 3,   "spring", GRASS_VAR1),
    (2, 12,  "spring", GRASS_VAR1),
    (3, 7,   "spring", GRASS_VAR1),
    (1, 14,  "spring", GRASS_VAR1),

    # Right margin grass variants.
    (23, 4,  "spring", GRASS_VAR1),
    (24, 12, "spring", GRASS_VAR1),
    (23, 8,  "spring", GRASS_VAR1),
    (31, 6,  "spring", GRASS_VAR1),

    # Left margin flowers/tufts.
    (1, 3,   "details", FLOWER_YEL),
    (2, 5,   "details", FLOWER_WHT),
    (0, 9,   "details", FLOWER_BLU),
    (1, 11,  "details", TUFT_A),
    (3, 5,   "details", TUFT_B),
    (3, 12,  "details", FLOWER_WHT),
    (0, 12,  "details", FLOWER_BLU),
    (2, 7,   "details", TUFT_C),
    (3, 11,  "details", TUFT_C),
    (1, 7,   "details", FLOWER_YEL),

    # Right margin flowers/tufts.
    (23, 3,  "details", FLOWER_WHT),
    (24, 5,  "details", FLOWER_YEL),
    (23, 11, "details", TUFT_A),
    (24, 9,  "details", TUFT_B),
    (23, 15, "details", FLOWER_BLU),
    (24, 13, "details", FLOWER_WHT),
    (31, 7,  "details", FLOWER_YEL),
    (24, 7,  "details", TUFT_C),
    (31, 12, "details", TUFT_A),
    (23, 14, "details", FLOWER_BLU),
]

# ---- Standalone sprite placements (pixel positions) -------------------------
# Each entry: (image_path, pixel_x, pixel_y) where (x, y) is the top-left of
# the sprite at its native size unless the renderer scales it.
#
# Coordinate budget:
#   Left  grass margin pixels: x in [0, 288).  Queue zone: x in [120, 280].
#   Right grass margin pixels: x in [736, 1024). Queue zone: x in [800, 960].
#   HUD top covers y in [0, 48). HUD bottom covers y in [560, 600).
#   Queue zone y in [80, 500] in both margins.
#
# Safe windows (outside queue, outside HUD):
#   Left  top:    x in [0, 120), y in [48, 80)
#   Left  bottom: x in [0, 120), y in [500, 560)
#   Right top:    x in [736, 800), y in [48, 80)
#   Right bottom: x in [736, 800) or x in [960, 1024), y in [500, 560)
#
# Tree (81x90) and house (~130x148 after scaling) are too tall to fit in
# the 32-px-tall top/bottom windows alone; we place them so their base sits
# above the bottom HUD and their top extends UP into the queue y-range only
# in x columns where there is no queue (i.e. on the very edges).

SPRITE_DECOS: list[tuple[Path, int, int]] = [
    # --- Trees (81x90) -----------------------------------------------------
    # Top-right tree, fully right of queue zone (x >= 960). Tree top tucks
    # into the HUD top region (y<48, covered at runtime).
    (TREE_PNG, 942, 6),

    # --- Corn stalks (28x61) ----------------------------------------------
    # Right margin bottom (y in [500, 560), x in [736, 800)). Fenced patch.
    (CORN_PNG, 745, 498),
    (CORN_PNG, 775, 498),
    # Right margin far bottom-right (x >= 960). Fenced patch.
    (CORN_PNG, 965, 498),
    (CORN_PNG, 995, 498),

    # --- Fences (76x22) ---------------------------------------------------
    # Each fence sits IN FRONT OF a crop patch so it reads as "fenced field"
    # rather than a stray fence post. No fences anywhere without crops behind.
    # In front of bottom-right corn patch (x in [736, 800)):
    (FENCE_PNG, 738, 478),
    # In front of far bottom-right corn patch (x >= 960):
    (FENCE_PNG, 958, 478),

    # --- Dirt patches (28x28) ---------------------------------------------
    # Tilled-soil patch, top-left margin (y<80, x<120). Placed as a 3-tile
    # row to read as a plowed strip.
    (DIRT_PNG, 20, 50),
    (DIRT_PNG, 50, 50),
    (DIRT_PNG, 80, 50),
    # Top-right margin tilled strip (y<80, x in [736, 800)):
    (DIRT_PNG, 740, 50),
    (DIRT_PNG, 770, 50),
]

# House is placed in render_background() with a custom scale.
HOUSE_X = 4              # left edge of house on canvas
HOUSE_BASE_Y = 560       # bottom edge of house sits just above bottom HUD
HOUSE_SCALE = 0.80       # 162x184 -> 130x147


def open_sheet(p: Path) -> Image.Image:
    return Image.open(p).convert("RGBA")


def get_tile(sheet: Image.Image, col: int, row: int) -> Image.Image:
    x, y = col * TILE, row * TILE
    return sheet.crop((x, y, x + TILE, y + TILE))


def dump_contact_sheet(sheet_path: Path, out_path: Path) -> None:
    sheet = open_sheet(sheet_path)
    sw, sh = sheet.size
    cols, rows = sw // TILE, sh // TILE
    scale = 2
    cell = TILE * scale
    label_h = 14
    out = Image.new("RGBA", (cols * cell, rows * (cell + label_h)), (32, 32, 32, 255))
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 10)
    except OSError:
        font = ImageFont.load_default()
    for r in range(rows):
        for c in range(cols):
            tile = get_tile(sheet, c, r).resize((cell, cell), Image.NEAREST)
            ox, oy = c * cell, r * (cell + label_h)
            out.paste(tile, (ox, oy), tile)
            draw.text((ox + 2, oy + cell), f"{c},{r}", fill=(255, 255, 255, 255), font=font)
    out.save(out_path)
    print(f"wrote {out_path}  ({cols}x{rows} tiles)")


def render_background() -> Path:
    spring  = open_sheet(SPRING_PNG)
    details = open_sheet(DETAILS_PNG)
    sheets = {"spring": spring, "details": details}

    grass_plain = get_tile(spring, *GRASS_PLAIN)
    lbank       = get_tile(spring, *LBANK_TILE)
    water       = get_tile(spring, *WATER_TILE)
    rbank       = get_tile(spring, *RBANK_TILE)

    bg = Image.new("RGBA", (W, H), (0, 0, 0, 255))

    # Pass 1: base terrain (grass + river).
    for r in range(ROWS):
        for c in range(COLS):
            if c < LBANK_COL:
                tile = grass_plain
            elif c == LBANK_COL:
                tile = lbank
            elif c < RBANK_COL:
                tile = water
            elif c == RBANK_COL:
                tile = rbank
            else:
                tile = grass_plain
            bg.paste(tile, (c * TILE, r * TILE), tile)

    # Pass 2: tile-grid decorations.
    for c, r, key, (sc, sr) in TILE_DECOS:
        tile = get_tile(sheets[key], sc, sr)
        bg.paste(tile, (c * TILE, r * TILE), tile)

    # Pass 3: dock/pier planks at the boat anchor row.
    log_l = get_tile(details, *LOG_LEFT)
    log_m = get_tile(details, *LOG_MID)
    log_r = get_tile(details, *LOG_RIGHT)
    bg.paste(log_l, (LEFT_PIER_COLS[0] * TILE, PIER_ROW * TILE), log_l)
    bg.paste(log_r, (LEFT_PIER_COLS[1] * TILE, PIER_ROW * TILE), log_r)
    bg.paste(log_l, (RIGHT_PIER_COLS[0] * TILE, PIER_ROW * TILE), log_l)
    bg.paste(log_r, (RIGHT_PIER_COLS[1] * TILE, PIER_ROW * TILE), log_r)
    # 2nd plank row up at the bank tiles only.
    bg.paste(log_m, (LEFT_PIER_COLS[0]  * TILE, (PIER_ROW - 1) * TILE), log_m)
    bg.paste(log_m, (RIGHT_PIER_COLS[1] * TILE, (PIER_ROW - 1) * TILE), log_m)

    # Pass 4: standalone sprite PNGs at hardcoded pixel positions.
    for path, px, py in SPRITE_DECOS:
        spr = Image.open(path).convert("RGBA")
        bg.paste(spr, (px, py), spr)

    # Pass 5: the requested farmhouse, bottom-left. Scaled to keep its right
    # edge inside the left grass margin (288 px wide).
    house = Image.open(HOUSE_PNG).convert("RGBA")
    new_size = (int(house.size[0] * HOUSE_SCALE), int(house.size[1] * HOUSE_SCALE))
    house = house.resize(new_size, Image.NEAREST)
    hx = HOUSE_X
    hy = HOUSE_BASE_Y - house.size[1]
    bg.paste(house, (hx, hy), house)

    # Output.
    out = OUT_DIR / "background_spring_1024x600.png"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    flat = Image.new("RGB", (W, H), (0, 0, 0))
    flat.paste(bg, (0, 0), bg)
    flat.save(out)
    print(f"wrote {out}")

    preview = flat.resize((W // 2, H // 2), Image.LANCZOS)
    preview_path = OUT_DIR / "background_preview.png"
    preview.save(preview_path)
    print(f"wrote {preview_path}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contact-sheet", action="store_true",
                    help="dump numbered grids of source tilesets; pick coords manually")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.contact_sheet:
        dump_contact_sheet(SPRING_PNG,  OUT_DIR / "_spring_grid.png")
        dump_contact_sheet(DETAILS_PNG, OUT_DIR / "_details_spring_grid.png")
        return

    render_background()


if __name__ == "__main__":
    main()
