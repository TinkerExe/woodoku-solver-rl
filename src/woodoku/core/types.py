from __future__ import annotations

from typing import TypeAlias

import numpy as np

BoardArray: TypeAlias = np.ndarray
PieceID: TypeAlias = int
MoveTuple: TypeAlias = tuple[PieceID, int, int]

BOARD_SIZE: int = 9
N_PIECES_PER_TURN: int = 3
