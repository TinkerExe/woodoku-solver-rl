from __future__ import annotations

import numpy as np

from woodoku.core.rules import get_legal_moves_mask
from woodoku.core.types import BOARD_SIZE, PieceID

from .action import ACTION_SPACE_SIZE, N_SLOTS


def action_masks_for(board: np.ndarray, pieces: list[PieceID], active: np.ndarray) -> np.ndarray:
    """Same masking rule as WoodokuEnv.action_masks — usable from screen inference without a gym.Env."""
    m = np.zeros(ACTION_SPACE_SIZE, dtype=bool)
    for slot in range(N_SLOTS):
        if not active[slot]:
            continue
        sub = get_legal_moves_mask(board, pieces[slot]).reshape(-1)
        base = slot * BOARD_SIZE * BOARD_SIZE
        m[base : base + BOARD_SIZE * BOARD_SIZE] = sub
    return m


def build_agent_obs(board: np.ndarray, pieces: list[PieceID], active: np.ndarray) -> dict[str, np.ndarray]:
    """Dict observation matching WoodokuEnv (uint8)."""
    from woodoku.env.observation import PIECE_OBS_DIM, piece_to_canvas

    z = np.zeros((PIECE_OBS_DIM, PIECE_OBS_DIM), dtype=np.uint8)
    pcs = np.stack([piece_to_canvas(pieces[i]) if active[i] else z for i in range(N_SLOTS)])
    return {"board": board.astype(np.uint8, copy=False).copy(), "pieces": pcs, "active": active.astype(np.uint8, copy=False).copy()}
