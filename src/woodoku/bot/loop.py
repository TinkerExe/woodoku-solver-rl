from __future__ import annotations

import time
import traceback

from woodoku.core.shapes import SHAPE_SIZES
from woodoku.solver.protocol import Solver
from .logger import log_game_over, log_turn, log_warning

RETRY_DELAY = 2.0
MAX_FAILURES = 10


def _detect_pieces(img, piece_rects, detect_piece_fn):
    ids = []
    for i, rect in enumerate(piece_rects):
        pid = detect_piece_fn(img, rect)
        if pid is None:
            print(f"  [warn] piece {i + 1} not detected")
            return None
        ids.append(pid)
    return ids


def run_loop(
    *,
    dry_run: bool = False,
    capture_fn=None,
    find_board_fn=None,
    read_board_fn=None,
    find_piece_areas_fn=None,
    detect_piece_fn=None,
    solve_fn=None,
    execute_fn=None,
    solver: Solver | None = None,
) -> None:
    consecutive_failures = 0
    turn = 0
    try:
        while True:
            img, window_offset = capture_fn()
            board_rect = find_board_fn(img)
            if board_rect is None:
                consecutive_failures += 1
                if consecutive_failures >= MAX_FAILURES:
                    break
                time.sleep(RETRY_DELAY)
                continue
            board_state = read_board_fn(img, board_rect)
            piece_rects = find_piece_areas_fn(img, board_rect)
            piece_ids = _detect_pieces(img, piece_rects, detect_piece_fn)
            if piece_ids is None:
                consecutive_failures += 1
                log_warning(f"Piece detection failed ({consecutive_failures}/{MAX_FAILURES})")
                if consecutive_failures >= MAX_FAILURES:
                    break
                time.sleep(RETRY_DELAY)
                continue
            consecutive_failures = 0
            turn += 1
            if solver is not None:
                moves = solver.solve(board_state, tuple(piece_ids))
            else:
                moves = solve_fn(board_state.tolist() if hasattr(board_state, "tolist") else board_state, piece_ids)
            if moves is None:
                log_game_over(turn)
                break
            print(moves)
            log_turn(turn, board_state, piece_ids, moves, SHAPE_SIZES)
            if not dry_run:
                execute_fn(moves, piece_ids, piece_rects, board_rect, window_offset, SHAPE_SIZES)
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
