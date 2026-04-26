from __future__ import annotations

import numpy as np

from woodoku.core.shapes import MAX_SHAPE_DIM, SHAPE_GRIDS
from woodoku.core.types import PieceID

PIECE_OBS_DIM = MAX_SHAPE_DIM
SCALARS_DIM = 31


def piece_to_canvas(shape_id: PieceID) -> np.ndarray:
    canvas = np.zeros((PIECE_OBS_DIM, PIECE_OBS_DIM), dtype=np.uint8)
    g = SHAPE_GRIDS[shape_id]
    canvas[: g.shape[0], : g.shape[1]] = g
    return canvas


def board_scalars(board: np.ndarray, pieces: list[PieceID], active: np.ndarray) -> np.ndarray:
    """31 normalized handcrafted features for obs v2."""
    b = board.astype(np.float32, copy=False)
    row_fill = b.mean(axis=1)  # 9
    col_fill = b.mean(axis=0)  # 9
    box_fill = []
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box_fill.append(float(b[br : br + 3, bc : bc + 3].mean()))
    legal_norm = np.zeros(3, dtype=np.float32)
    if pieces:
        from woodoku.core.rules import get_legal_moves_mask

        for i in range(min(3, len(pieces))):
            if active[i]:
                legal_norm[i] = float(get_legal_moves_mask(board, pieces[i]).sum()) / 81.0
    density = np.array([float(b.mean())], dtype=np.float32)
    out = np.concatenate(
        [
            row_fill.astype(np.float32, copy=False),
            col_fill.astype(np.float32, copy=False),
            np.asarray(box_fill, dtype=np.float32),
            legal_norm,
            density,
        ]
    )
    assert out.shape == (SCALARS_DIM,)
    return out.astype(np.float32, copy=False)
