from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from woodoku.core.rules import get_legal_moves_mask


@dataclass(frozen=True)
class RewardConfigV2:
    survive_bonus: float = 0.05
    progress_scale: float = 0.20
    mobility_scale: float = 0.10
    terminal_penalty: float = -1.5


def line_progress(board: np.ndarray) -> float:
    """Progress proxy in [0, 27]: rows + cols + 3x3 boxes occupancy fractions."""
    b = board.astype(np.float32, copy=False)
    row_fill = b.mean(axis=1)  # 9
    col_fill = b.mean(axis=0)  # 9
    box_fill: list[float] = []
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box_fill.append(float(b[br : br + 3, bc : bc + 3].mean()))
    return float(row_fill.sum() + col_fill.sum() + np.sum(box_fill))


def legal_moves_norm(board: np.ndarray, piece_ids: tuple[int, ...]) -> float:
    """Normalized mobility for a set of pieces in [0, 1]."""
    if not piece_ids:
        return 0.0
    total = 0
    for sid in piece_ids:
        total += int(get_legal_moves_mask(board, sid).sum())
    # Each piece has at most 81 top-left placements.
    return float(total) / float(81 * len(piece_ids))


def reward_v1(n_placed: int, n_cleared: int) -> float:
    return float(n_placed + 2 * n_cleared)


def reward_v2(
    *,
    before_board: np.ndarray,
    after_board: np.ndarray,
    n_placed: int,
    n_cleared: int,
    terminated: bool,
    remaining_piece_ids_before: tuple[int, ...],
    remaining_piece_ids_after: tuple[int, ...],
    cfg: RewardConfigV2 = RewardConfigV2(),
) -> float:
    """Shaped reward while keeping base score term compatible with v1."""
    base = reward_v1(n_placed, n_cleared)
    survive = cfg.survive_bonus
    progress = cfg.progress_scale * (line_progress(after_board) - line_progress(before_board))
    # Mobility is only comparable when the remaining piece set does not change.
    if remaining_piece_ids_before == remaining_piece_ids_after and remaining_piece_ids_after:
        m_before = legal_moves_norm(before_board, remaining_piece_ids_before)
        m_after = legal_moves_norm(after_board, remaining_piece_ids_after)
        mobility = cfg.mobility_scale * (m_after - m_before)
    else:
        mobility = 0.0
    terminal = cfg.terminal_penalty if terminated else 0.0
    return float(base + survive + progress + mobility + terminal)

