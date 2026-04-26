from __future__ import annotations

from typing import Protocol

from woodoku.core.types import BoardArray, MoveTuple, PieceID
from woodoku.solver.go_bridge import close, solve


class Solver(Protocol):
    def solve(self, board: BoardArray, pieces: tuple[PieceID, PieceID, PieceID]) -> list[MoveTuple] | None: ...
    def close(self) -> None: ...


class GoSolver:
    def solve(self, board: BoardArray, pieces: tuple[PieceID, PieceID, PieceID]) -> list[MoveTuple] | None:
        return solve(board.tolist(), list(pieces))

    def close(self) -> None:
        close()
