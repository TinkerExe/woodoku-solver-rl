"""
Board and piece detection from a BGR screenshot of Woodoku running in BlueStacks.

Colour observations from the game screenshot:
  - Empty board cell : dark reddish-brown  (HSV H≈5-20, S≈45-70, V≈25-55)
  - Filled cell/piece: light beige/cream   (HSV H≈25-45, S≈25-55, V≈65-90)
  - UI background    : medium wood brown   (between the two above)

Strategy
--------
1. find_board()   – threshold for the dark-cell colour, find the largest
                    near-square region → board bounding rect.
2. read_board()   – sample centre pixel of each of the 81 cells; bright = filled.
3. find_piece_areas() – crop below the board, split into 3 horizontal zones.
4. detect_piece_id()  – find light-pixel blobs in each zone, quantise to a grid,
                        normalise and look up in CELLS_TO_ID.
"""

from __future__ import annotations
import numpy as np
import cv2
from .shapes import CELLS_TO_ID

# ── colour thresholds (HSV, 0-179 / 0-255 / 0-255) ──────────────────────────
# "piece / filled-cell" colour: light beige
# Adjust _PIECE_HSV_LO/HI if piece detection is wrong
_PIECE_HSV_LO = np.array([15,  30, 140], dtype=np.uint8)
_PIECE_HSV_HI = np.array([50, 200, 255], dtype=np.uint8)

# "empty board cell" colour: dark reddish-brown (both dark and lighter 3x3 blocks)
# Top rows of the board are very dark (V≈30-50), bottom rows medium (V≈100-160).
# UI background is lighter (V≈180+), so V_HI=170 keeps it out.
# Adjust _CELL_HSV_LO/HI if board is not detected
_CELL_HSV_LO  = np.array([ 0,  50,  15], dtype=np.uint8)
_CELL_HSV_HI  = np.array([25, 230, 170], dtype=np.uint8)

# minimum area (px²) for a blob to be considered a piece cell
_MIN_BLOB_AREA = 10


# ── helpers ──────────────────────────────────────────────────────────────────

def _piece_mask(bgr: np.ndarray) -> np.ndarray:
    """Binary mask: 255 where pixels match the light beige piece colour."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, _PIECE_HSV_LO, _PIECE_HSV_HI)


def _cell_mask(bgr: np.ndarray) -> np.ndarray:
    """Binary mask: 255 where pixels match the dark board-cell colour."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, _CELL_HSV_LO, _CELL_HSV_HI)


def _normalize_cells(cells: set[tuple[int,int]]) -> frozenset[tuple[int,int]]:
    if not cells:
        return frozenset()
    min_r = min(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    return frozenset((r - min_r, c - min_c) for r, c in cells)


# ── board layout constants (fractions of the game content area) ───────────────
# Tune these if the board rectangle is off.
# Measured from screenshots: game area is the non-black portrait strip in BlueStacks.
BOARD_LEFT_FRAC   = 0.03   # board left  edge as fraction of game width
BOARD_TOP_FRAC    = 0.17   # board top   edge as fraction of game height
BOARD_WIDTH_FRAC  = 0.94   # board width as fraction of game width
# Board is a perfect square: height == width (forced below)


def _find_game_area(img: np.ndarray) -> tuple[int,int,int,int]:
    """
    Return (x, y, w, h) of the game content area (excludes letterbox black bars).

    Uses column density: a column belongs to the game area only if at least
    30 % of its pixels are non-black.  A thin BlueStacks toolbar spanning the
    full width doesn't pass this test, so it won't inflate gw.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h_img, w_img = gray.shape

    # Count non-black pixels per column
    col_density = np.sum(gray > 25, axis=0).astype(np.float32)
    threshold   = h_img * 0.30          # 30 % of column height

    game_cols = np.where(col_density > threshold)[0]
    if len(game_cols) == 0:
        return 0, 0, w_img, h_img

    gx = int(game_cols[0])
    gw = int(game_cols[-1]) - gx + 1
    return gx, 0, gw, h_img


def find_board(img: np.ndarray) -> tuple[int,int,int,int] | None:
    """
    Return (x, y, w, h) of the 9×9 board in *img*.
    Uses hardcoded fractions inside the non-black game area.
    The board is always forced to be square (h == w).
    """
    gx, gy, gw, gh = _find_game_area(img)

    size = int(gw * BOARD_WIDTH_FRAC)          # square side length
    bx   = gx + int(gw * BOARD_LEFT_FRAC)
    by   = gy + int(gh * BOARD_TOP_FRAC) + size // 18  # +½ cell down

    # Clamp to image bounds
    h_img, w_img = img.shape[:2]
    bx = max(0, min(bx, w_img - size))
    by = max(0, min(by, h_img - size))

    return bx, by, size, size


def board_cell_debug_mask(img: np.ndarray) -> np.ndarray:
    """Return the raw cell colour mask — useful for calibration."""
    return _cell_mask(img)


def piece_color_debug_mask(img: np.ndarray) -> np.ndarray:
    """Return the raw piece colour mask — useful for calibration."""
    return _piece_mask(img)


# ── board reading ─────────────────────────────────────────────────────────────

def read_board(img: np.ndarray, board_rect: tuple[int,int,int,int]) -> list[list[int]]:
    """
    Return a 9×9 list of 0/1 by sampling the centre of each cell.
    A cell is considered 'filled' if its centre pixel matches the piece colour.
    """
    x, y, w, h = board_rect
    cell_w = w / 9.0
    cell_h = h / 9.0
    piece_mask = _piece_mask(img)

    board: list[list[int]] = []
    for row in range(9):
        board_row: list[int] = []
        for col in range(9):
            # Sample a small 5×5 patch at the cell centre
            cx = int(x + (col + 0.5) * cell_w)
            cy = int(y + (row + 0.5) * cell_h)
            patch = piece_mask[
                max(0, cy-3):cy+4,
                max(0, cx-3):cx+4
            ]
            filled = int(np.mean(patch) > 64)   # >25% bright = filled
            board_row.append(filled)
        board.append(board_row)
    return board


# ── piece area detection ──────────────────────────────────────────────────────

def find_piece_areas(
    img: np.ndarray,
    board_rect: tuple[int,int,int,int]
) -> list[tuple[int,int,int,int]]:
    """
    Return 3 (x, y, w, h) rects for the piece zones below the board.
    Each zone is 1/3 of the BOARD width, aligned with the board left edge.
    Height = 40 % of the board size (pieces are rendered in that strip).
    """
    bx, by, bw, bh = board_rect
    top_skip    = int(bh * 0.40) // 3   # fixed gap between board and pieces
    zone_height = int(bh * 0.425)
    zone_top    = by + bh + top_skip - int(zone_height * 0.15)
    zone_width  = bw // 3

    return [
        (bx + i * zone_width, zone_top, zone_width, zone_height)
        for i in range(3)
    ]


def detect_piece_id(img: np.ndarray, piece_rect: tuple[int,int,int,int]) -> int | None:
    """
    Detect the shape ID of the piece shown in *piece_rect*.
    Returns the matching shape ID from CELLS_TO_ID, or None on failure.
    """
    px, py, pw, ph = piece_rect
    crop = img[py:py+ph, px:px+pw]
    if crop.size == 0:
        return None

    mask = _piece_mask(crop)
    # only open (remove small noise); NO close — it merges adjacent cells
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

    # collect valid blob centres (skip background label 0)
    centers: list[tuple[float,float]] = []
    blob_sizes: list[float] = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < _MIN_BLOB_AREA:
            continue
        cx, cy = centroids[i]
        centers.append((cx, cy))
        bw_b = stats[i, cv2.CC_STAT_WIDTH]
        bh_b = stats[i, cv2.CC_STAT_HEIGHT]
        blob_sizes.append((bw_b + bh_b) / 2.0)

    if not centers:
        return None

    # Estimate cell size: use median blob height (more reliable for vertical pieces)
    blob_heights = [stats[i, cv2.CC_STAT_HEIGHT]
                    for i in range(1, num_labels)
                    if stats[i, cv2.CC_STAT_AREA] >= _MIN_BLOB_AREA]
    cell_size = float(np.median(blob_heights)) if blob_heights else float(np.median(blob_sizes))
    cell_size = max(cell_size, 5.0)

    min_x = min(c[0] for c in centers)
    min_y = min(c[1] for c in centers)

    def _quantise(cs: float) -> frozenset[tuple[int,int]]:
        cells: set[tuple[int,int]] = set()
        for cx, cy in centers:
            cells.add((round((cy - min_y) / cs), round((cx - min_x) / cs)))
        return _normalize_cells(cells)

    # Try cell_size and a range of scaled variants to handle estimation error
    for factor in (1.0, 0.85, 1.15, 0.70, 1.30, 0.55, 1.50):
        result = CELLS_TO_ID.get(_quantise(cell_size * factor))
        if result is not None:
            return result
    return None
