"""
Structured turn-by-turn log for the Woodoku bot.

Writes to woodoku_bot.log in the project root.
Each turn records: timestamp, detected pieces, board state, solver moves.
"""

from __future__ import annotations
import logging
import os
from datetime import datetime

_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "woodoku_bot.log")

_logger = logging.getLogger("woodoku")
_logger.setLevel(logging.DEBUG)
if not _logger.handlers:
    fh = logging.FileHandler(_LOG_PATH, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(fh)


def _board_str(board: list[list[int]]) -> str:
    lines = []
    for r, row in enumerate(board):
        if r > 0 and r % 3 == 0:
            lines.append("  ·  ·  ·  ·  ·  ·  ·  ·  ·")
        lines.append("  " + " ".join("■" if v else "·" for v in row))
    return "\n".join(lines)


def log_turn(
    turn: int,
    board_before: list[list[int]],
    piece_ids: list[int],
    moves: list[tuple[int, int, int]],
    shape_sizes: dict[int, tuple[int, int]],
) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"\n{'='*52}",
        f"TURN {turn}  [{ts}]",
        f"{'='*52}",
        f"Pieces:  {piece_ids}",
        "Board before:",
        _board_str(board_before),
        "Moves:",
    ]
    for i, (shape_id, row, col) in enumerate(moves, 1):
        h, w = shape_sizes.get(shape_id, (1, 1))
        lines.append(f"  {i}. shape {shape_id:3d} ({h}×{w})  →  row={row}, col={col}")
    _logger.info("\n".join(lines))


def log_warning(msg: str) -> None:
    _logger.warning(f"[WARN] {msg}")


def log_game_over(turn: int) -> None:
    _logger.info(f"\n{'='*52}\nGAME OVER after {turn} turns\n{'='*52}")
