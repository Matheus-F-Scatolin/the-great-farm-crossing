"""Shared constants for the UI."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ASSETS = REPO / "assets"

WINDOW_W = 1024
WINDOW_H = 600
TILE = 32

# Layout from tools/render_background.py.
GRASS_LEFT_END_COL = 11   # cols [0, 11) are grass
WATER_END_COL = 21        # cols [11, 21) are water
# cols [21, 32) are grass right

# Boat dock anchor points (pixel center where boat sprite is placed).
# Boat sprites are ~125 wide x ~64 tall. We anchor center-x to these columns.
LEFT_DOCK_X = (GRASS_LEFT_END_COL - 1) * TILE + TILE // 2   # ~336 px
RIGHT_DOCK_X = WATER_END_COL * TILE + TILE // 2             # ~688 px
BOAT_Y = 9 * TILE                                            # row 9 center band

# HUD bars.
HUD_TOP_H = 48
HUD_BOTTOM_H = 40

# Character idle frame coords on their sheets (col, row) and frame sizes.
FARMER_FRAME = (32, 64)
FARMER_IDLE = (1, 0)
SHEEP_FRAME = (32, 32)
SHEEP_IDLE = (1, 0)
FOX_FRAME = (48, 64)
FOX_IDLE = (1, 0)

# Per-type display widths (pixels). We scale each sprite to this width so all
# three look proportional side-by-side on the boat (~125 px wide, 3 passengers).
# Native frame widths differ (farmer 32, sheep 32, fox 48), so heights end up
# slightly different to match the natural proportions of each sheet.
FARMER_TARGET_W = 40
SHEEP_TARGET_W = 40
FOX_TARGET_W = 80

# Replay speed bounds.
MIN_SPEED = 0.25
MAX_SPEED = 4.0
DEFAULT_SPEED = 1.0
