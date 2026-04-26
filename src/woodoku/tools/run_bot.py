from __future__ import annotations

import sys

from woodoku.automation.mouse import execute_moves
from woodoku.bot.loop import run_loop
from woodoku.capture.screen import get_game_image
from woodoku.recognition.cv_classifier import detect_piece_id, read_board
from woodoku.recognition.geometry import find_board, find_piece_areas
from woodoku.solver.go_bridge import close as solver_close
from woodoku.solver.go_bridge import solve


def main() -> None:
    dry = "--dry" in sys.argv
    try:
        run_loop(
            dry_run=dry,
            capture_fn=get_game_image,
            find_board_fn=find_board,
            read_board_fn=read_board,
            find_piece_areas_fn=find_piece_areas,
            detect_piece_fn=detect_piece_id,
            solve_fn=solve,
            execute_fn=execute_moves,
        )
    finally:
        solver_close()


if __name__ == "__main__":
    main()
