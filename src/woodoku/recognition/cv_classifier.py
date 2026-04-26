from __future__ import annotations

import cv2
import numpy as np

from woodoku.core.shapes import CELLS_TO_ID
from .masks import _piece_mask

_MIN_BLOB_AREA = 4


def _normalize_cells(cells: set[tuple[int, int]]) -> frozenset[tuple[int, int]]:
    if not cells:
        return frozenset()
    min_r = min(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    return frozenset((r - min_r, c - min_c) for r, c in cells)


def read_board(img: np.ndarray, board_rect: tuple[int, int, int, int]) -> np.ndarray:
    x, y, w, h = board_rect
    cell_w = w / 9.0
    cell_h = h / 9.0
    piece_mask = _piece_mask(img)
    board = np.zeros((9, 9), dtype=np.uint8)
    for row in range(9):
        for col in range(9):
            cx = int(x + (col + 0.5) * cell_w)
            cy = int(y + (row + 0.5) * cell_h)
            patch = piece_mask[max(0, cy - 3) : cy + 4, max(0, cx - 3) : cx + 4]
            if patch.size == 0:
                board[row, col] = 0
            else:
                board[row, col] = int(np.mean(patch) > 64)
    return board


def detect_piece_id(img: np.ndarray, piece_rect: tuple[int, int, int, int]) -> int | None:
    px, py, pw, ph = piece_rect
    crop = img[py : py + ph, px : px + pw]
    if crop.size == 0:
        return None
    mask = _piece_mask(crop)
    # Keep tiny piece blocks; 3x3 opening can erase them at smaller render scales.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    centers: list[tuple[float, float]] = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= _MIN_BLOB_AREA:
            cx, cy = centroids[i]
            centers.append((cx, cy))
    if not centers:
        return None
    blob_heights = [stats[i, cv2.CC_STAT_HEIGHT] for i in range(1, num_labels) if stats[i, cv2.CC_STAT_AREA] >= _MIN_BLOB_AREA]
    cell_size = float(np.median(blob_heights)) if blob_heights else 5.0
    cell_size = max(cell_size, 5.0)
    min_x = min(c[0] for c in centers)
    min_y = min(c[1] for c in centers)

    def _quantise(cs: float) -> frozenset[tuple[int, int]]:
        cells: set[tuple[int, int]] = set()
        for cx, cy in centers:
            cells.add((round((cy - min_y) / cs), round((cx - min_x) / cs)))
        return _normalize_cells(cells)

    for factor in (1.0, 0.85, 1.15, 0.70, 1.30, 0.55, 1.50):
        sid = CELLS_TO_ID.get(_quantise(cell_size * factor))
        if sid is not None:
            return sid
    return None
