from __future__ import annotations

from woodoku.core.types import BOARD_SIZE

N_SLOTS = 3
ACTION_SPACE_SIZE = N_SLOTS * BOARD_SIZE * BOARD_SIZE


def encode(slot: int, row: int, col: int) -> int:
    return slot * BOARD_SIZE * BOARD_SIZE + row * BOARD_SIZE + col


def decode(action: int) -> tuple[int, int, int]:
    slot, rem = divmod(action, BOARD_SIZE * BOARD_SIZE)
    row, col = divmod(rem, BOARD_SIZE)
    return slot, row, col
