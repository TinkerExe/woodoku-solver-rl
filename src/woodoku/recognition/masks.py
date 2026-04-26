from __future__ import annotations

import cv2
import numpy as np

_PIECE_HSV_LO = np.array([12, 20, 170], dtype=np.uint8)
_PIECE_HSV_HI = np.array([40, 120, 255], dtype=np.uint8)
_CELL_HSV_LO = np.array([0, 50, 15], dtype=np.uint8)
_CELL_HSV_HI = np.array([25, 230, 170], dtype=np.uint8)


def _piece_mask(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, _PIECE_HSV_LO, _PIECE_HSV_HI)


def _cell_mask(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, _CELL_HSV_LO, _CELL_HSV_HI)


def piece_color_debug_mask(img: np.ndarray) -> np.ndarray:
    return _piece_mask(img)


def board_cell_debug_mask(img: np.ndarray) -> np.ndarray:
    return _cell_mask(img)
