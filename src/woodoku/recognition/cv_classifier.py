from __future__ import annotations

import cv2
import numpy as np

from woodoku.core.shapes import CELLS_TO_ID
from .masks import _piece_mask

_MIN_BLOB_AREA = 4
# Ignore blobs whose centroid sits in the outer strip (neighbour piece from overlapping crops).
_EDGE_FRAC = 0.11


def _normalize_cells(cells: set[tuple[int, int]]) -> frozenset[tuple[int, int]]:
    if not cells:
        return frozenset()
    min_r = min(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    return frozenset((r - min_r, c - min_c) for r, c in cells)


def _cells_from_binary_mask(mask: np.ndarray, cell_size: float) -> frozenset[tuple[int, int]]:
    """Snap occupied pixels to a coarse grid (fallback when one CC = whole piece)."""
    ys, xs = np.where(mask > 0)
    if len(ys) == 0:
        return frozenset()
    min_y, min_x = float(ys.min()), float(xs.min())
    cells: set[tuple[int, int]] = set()
    cs = max(float(cell_size), 4.0)
    for y, x in zip(ys, xs):
        cells.add((int(round((float(y) - min_y) / cs)), int(round((float(x) - min_x) / cs))))
    return _normalize_cells(cells)


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
    close_k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_k)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    lo_x, hi_x = pw * _EDGE_FRAC, pw * (1.0 - _EDGE_FRAC)
    lo_y, hi_y = ph * _EDGE_FRAC, ph * (1.0 - _EDGE_FRAC)
    candidates: list[int] = []
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] < _MIN_BLOB_AREA:
            continue
        cx, cy = float(centroids[i][0]), float(centroids[i][1])
        if lo_x <= cx <= hi_x and lo_y <= cy <= hi_y:
            candidates.append(i)
    if not candidates:
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= _MIN_BLOB_AREA:
                candidates.append(i)
    if not candidates:
        return None
    cx0, cy0 = pw / 2.0, ph / 2.0

    def _dist2(i: int) -> float:
        cx, cy = float(centroids[i][0]), float(centroids[i][1])
        return (cx - cx0) ** 2 + (cy - cy0) ** 2

    # Union all in-field blobs (one physical piece can split into several CCs after morphology).
    piece_mask = np.zeros((ph, pw), dtype=np.uint8)
    for i in candidates:
        piece_mask = np.maximum(piece_mask, (labels == i).astype(np.uint8) * 255)
    centers = [(float(centroids[i][0]), float(centroids[i][1])) for i in candidates if stats[i, cv2.CC_STAT_AREA] >= _MIN_BLOB_AREA]
    if not centers:
        return None
    blob_heights = [stats[i, cv2.CC_STAT_HEIGHT] for i in candidates if stats[i, cv2.CC_STAT_AREA] >= _MIN_BLOB_AREA]
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
    # Whole piece merged into one blob: infer grid from pixel coverage.
    for factor in (1.0, 0.85, 1.15, 0.70, 1.30, 0.55, 1.50):
        cs = cell_size * factor
        sid = CELLS_TO_ID.get(_cells_from_binary_mask(piece_mask, cs))
        if sid is not None:
            return sid
    return None
