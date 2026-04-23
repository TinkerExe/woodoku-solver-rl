"""
Main game loop: capture → detect → solve → click, repeat.

Usage (from project root):
    go build -o woodoku-solver.exe .
    python -m vision.main

Press Ctrl+C to stop.  Move mouse to top-left corner for emergency abort.
"""

from __future__ import annotations
import sys
import time
import traceback

from vision.capture   import get_game_image
from vision.detector  import find_board, read_board, find_piece_areas, detect_piece_id
from vision.solver    import solve, close as solver_close
from vision.automator import execute_moves
from vision.shapes    import SHAPE_SIZE
from vision.logger    import log_turn, log_warning, log_game_over


# How long to wait before re-trying if detection fails
RETRY_DELAY = 2.0
# How many consecutive detection failures before giving up
MAX_FAILURES = 10


def _detect_pieces(
    img,
    piece_rects: list,
) -> list[int] | None:
    """Detect all 3 piece IDs; return None if any fails."""
    ids = []
    for i, rect in enumerate(piece_rects):
        pid = detect_piece_id(img, rect)
        if pid is None:
            print(f"  [warn] piece {i+1} not detected")
            return None
        ids.append(pid)
    return ids


def run_loop(dry_run: bool = False) -> None:
    """
    Main automation loop.
    dry_run=True: detect and solve but don't click (safe for testing).
    """
    print("Starting Woodoku CV bot …  (Ctrl+C to quit, mouse top-left to abort)")
    if dry_run:
        print("DRY RUN: moves will be printed but not executed.")

    consecutive_failures = 0
    turn = 0

    try:
        while True:
            # ── 1. capture ───────────────────────────────────────────────────
            img, window_offset = get_game_image()

            # ── 2. find board ────────────────────────────────────────────────
            board_rect = find_board(img)
            if board_rect is None:
                consecutive_failures += 1
                print(f"[{consecutive_failures}/{MAX_FAILURES}] Board not found — is Woodoku visible?")
                if consecutive_failures >= MAX_FAILURES:
                    print("Too many failures, stopping.")
                    break
                time.sleep(RETRY_DELAY)
                continue

            # ── 3. read board state ──────────────────────────────────────────
            board_state = read_board(img, board_rect)

            # ── 4. find & detect pieces ──────────────────────────────────────
            piece_rects = find_piece_areas(img, board_rect)
            piece_ids   = _detect_pieces(img, piece_rects)
            if piece_ids is None:
                consecutive_failures += 1
                msg = f"Piece detection failed ({consecutive_failures}/{MAX_FAILURES})"
                print(f"[{consecutive_failures}/{MAX_FAILURES}] Piece detection failed — retrying …")
                log_warning(msg)
                if consecutive_failures >= MAX_FAILURES:
                    print("Too many failures, stopping.")
                    break
                time.sleep(RETRY_DELAY)
                continue

            consecutive_failures = 0
            turn += 1
            print(f"\n=== Turn {turn} ===  pieces: {piece_ids}")

            # ── 5. solve ─────────────────────────────────────────────────────
            moves = solve(board_state, piece_ids)
            if moves is None:
                print("Solver says GAME OVER (or no valid moves).")
                log_game_over(turn)
                break

            for shape_id, row, col in moves:
                h, w = SHAPE_SIZE.get(shape_id, (1, 1))
                print(f"  shape {shape_id:3d} ({h}×{w}) → board[{row}][{col}]")

            log_turn(turn, board_state, piece_ids, moves, SHAPE_SIZE)

            # ── 6. execute ───────────────────────────────────────────────────
            if not dry_run:
                execute_moves(
                    moves,
                    piece_ids,
                    piece_rects,
                    board_rect,
                    window_offset,
                    SHAPE_SIZE,
                )

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception:
        traceback.print_exc()
    finally:
        solver_close()


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    run_loop(dry_run=dry)
