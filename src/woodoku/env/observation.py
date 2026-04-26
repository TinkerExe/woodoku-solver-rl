from __future__ import annotations

import numpy as np

from woodoku.core.shapes import MAX_SHAPE_DIM, SHAPE_GRIDS
from woodoku.core.types import PieceID

PIECE_OBS_DIM = MAX_SHAPE_DIM


def piece_to_canvas(shape_id: PieceID) -> np.ndarray:
    canvas = np.zeros((PIECE_OBS_DIM, PIECE_OBS_DIM), dtype=np.uint8)
    g = SHAPE_GRIDS[shape_id]
    canvas[: g.shape[0], : g.shape[1]] = g
    return canvas
