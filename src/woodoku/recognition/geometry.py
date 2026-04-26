from __future__ import annotations

import cv2
import numpy as np

# Calibrated defaults for BlueStacks portrait window.
BOARD_LEFT_FRAC = 0.03
BOARD_TOP_FRAC = 0.16
BOARD_WIDTH_FRAC = 0.95


def _find_game_area(img: np.ndarray) -> tuple[int, int, int, int]:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_img, w_img = hsv.shape[:2]
    # Woodoku board/theme is mostly warm brown. This excludes dark IDE side panes.
    wood_mask = ((hsv[:, :, 0] <= 35) & (hsv[:, :, 1] >= 40) & (hsv[:, :, 2] >= 35))
    col_density = np.sum(wood_mask, axis=0).astype(np.float32)
    wood_cols = np.where(col_density > h_img * 0.25)[0]
    if len(wood_cols) > 0:
        gx = int(wood_cols[0])
        gw = int(wood_cols[-1]) - gx + 1
        return gx, 0, gw, h_img

    # Fallback for unexpected themes/lighting.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    col_density = np.sum(gray > 25, axis=0).astype(np.float32)
    game_cols = np.where(col_density > h_img * 0.30)[0]
    if len(game_cols) == 0:
        return 0, 0, w_img, h_img
    gx = int(game_cols[0])
    gw = int(game_cols[-1]) - gx + 1
    return gx, 0, gw, h_img


def find_board(img: np.ndarray) -> tuple[int, int, int, int] | None:
    gx, gy, gw, gh = _find_game_area(img)
    size = int(gw * BOARD_WIDTH_FRAC)
    bx = gx + int(gw * BOARD_LEFT_FRAC)
    by = gy + int(gh * BOARD_TOP_FRAC) + size // 18
    h_img, w_img = img.shape[:2]
    bx = max(0, min(bx, w_img - size))
    by = max(0, min(by, h_img - size))
    return bx, by, size, size


def find_piece_areas(img: np.ndarray, board_rect: tuple[int, int, int, int]) -> list[tuple[int, int, int, int]]:
    bx, by, bw, bh = board_rect
    zone_height = int(bh * 0.35)
    zone_top = by + bh + int(bh * 0.1)
    zone_width = bw // 3
    h_img, w_img = img.shape[:2]
    rects: list[tuple[int, int, int, int]] = []
    for i in range(3):
        x = bx + i * zone_width
        y = zone_top
        x0 = max(0, min(x, w_img))
        y0 = max(0, min(y, h_img))
        x1 = max(x0, min(x + zone_width, w_img))
        y1 = max(y0, min(y + zone_height, h_img))
        rects.append((x0, y0, x1 - x0, y1 - y0))
    return rects
