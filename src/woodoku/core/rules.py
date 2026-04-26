from __future__ import annotations

import numpy as np

from .shapes import SHAPE_GRIDS, SHAPE_SIZES
from .types import BOARD_SIZE, BoardArray, PieceID


def is_legal_move(board: BoardArray, shape_id: PieceID, row: int, col: int) -> bool:
    h, w = SHAPE_SIZES[shape_id]
    if row < 0 or col < 0 or row + h > BOARD_SIZE or col + w > BOARD_SIZE:
        return False
    grid = SHAPE_GRIDS[shape_id]
    region = board[row : row + h, col : col + w]
    return not np.any((grid == 1) & (region == 1))


def get_legal_moves_mask(board: BoardArray, shape_id: PieceID) -> np.ndarray:
    h, w = SHAPE_SIZES[shape_id]
    mask = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=bool)
    grid = SHAPE_GRIDS[shape_id].astype(bool)
    for r in range(BOARD_SIZE - h + 1):
        for c in range(BOARD_SIZE - w + 1):
            region = board[r : r + h, c : c + w]
            if not np.any(grid & (region == 1)):
                mask[r, c] = True
    return mask


def _check_and_clear(board: BoardArray) -> tuple[BoardArray, int]:
    to_clear = np.zeros_like(board, dtype=bool)
    full_rows = np.all(board == 1, axis=1)
    to_clear[full_rows, :] = True
    full_cols = np.all(board == 1, axis=0)
    to_clear[:, full_cols] = True
    for br in range(0, BOARD_SIZE, 3):
        for bc in range(0, BOARD_SIZE, 3):
            if np.all(board[br : br + 3, bc : bc + 3] == 1):
                to_clear[br : br + 3, bc : bc + 3] = True
    n = int(to_clear.sum())
    new_board = board.copy()
    new_board[to_clear] = 0
    return new_board, n


def apply_move(board: BoardArray, shape_id: PieceID, row: int, col: int) -> tuple[BoardArray, int, int]:
    if not is_legal_move(board, shape_id, row, col):
        raise ValueError(f"illegal move: shape={shape_id} at ({row}, {col})")
    h, w = SHAPE_SIZES[shape_id]
    grid = SHAPE_GRIDS[shape_id]
    new_board = board.copy()
    new_board[row : row + h, col : col + w] |= grid
    n_placed = int(grid.sum())
    new_board, n_cleared = _check_and_clear(new_board)
    return new_board, n_placed, n_cleared


def score_for_move(n_placed: int, n_cleared: int) -> float:
    return float(n_placed + 2 * n_cleared)


def is_terminal(board: BoardArray, available_pieces: tuple[PieceID, ...]) -> bool:
    if not available_pieces:
        return True
    for sid in available_pieces:
        if get_legal_moves_mask(board, sid).any():
            return False
    return True


def empty_board() -> BoardArray:
    return np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.uint8)
