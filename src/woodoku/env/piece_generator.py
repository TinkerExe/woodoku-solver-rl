from __future__ import annotations

import random
from typing import Protocol

from woodoku.core.shapes import ALL_SHAPE_IDS
from woodoku.core.types import PieceID


class PieceGenerator(Protocol):
    def reset(self, seed: int | None = None) -> None: ...
    def next_three(self) -> tuple[PieceID, PieceID, PieceID]: ...


class UniformGenerator:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def reset(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def next_three(self) -> tuple[PieceID, PieceID, PieceID]:
        ids = ALL_SHAPE_IDS
        return (
            ids[self._rng.randrange(len(ids))],
            ids[self._rng.randrange(len(ids))],
            ids[self._rng.randrange(len(ids))],
        )


class FixedGenerator:
    def __init__(self, triples: list[tuple[PieceID, PieceID, PieceID]]) -> None:
        self._triples = list(triples)
        self._i = 0

    def reset(self, seed: int | None = None) -> None:
        self._i = 0

    def next_three(self) -> tuple[PieceID, PieceID, PieceID]:
        if self._i >= len(self._triples):
            raise IndexError("FixedGenerator exhausted")
        t = self._triples[self._i]
        self._i += 1
        return t
