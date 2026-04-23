"""
Integration with the Go solver binary (woodoku-solver.exe -cv).

The binary runs in a persistent subprocess; each turn we pipe:
  9 lines of board state  (space-separated 0/1 per row)
  1 line of 3 piece IDs

And read back:
  3 lines "shapeID row col"
  1 line  "DONE"
  or      "GAME_OVER"
"""

from __future__ import annotations
import os
import subprocess
import sys

_BINARY_REL = os.path.join(os.path.dirname(__file__), "..", "woodoku-solver.exe")

def _resolve_binary() -> str:
    """Return the path to the Go binary, handling WSL → Windows path translation."""
    path = os.path.abspath(_BINARY_REL)
    if not os.path.exists(path) and os.path.exists("/proc/version"):
        # Running in WSL: try to convert Windows path via wslpath
        try:
            r = __import__("subprocess").run(
                ["wslpath", "-u", path.replace("\\", "/")],
                capture_output=True, text=True
            )
            wsl_path = r.stdout.strip()
            if wsl_path and os.path.exists(wsl_path):
                return wsl_path
        except Exception:
            pass
    return path

_BINARY = _resolve_binary()
_proc: subprocess.Popen | None = None


def _start() -> subprocess.Popen:
    binary = os.path.abspath(_BINARY)
    if not os.path.exists(binary):
        raise FileNotFoundError(
            f"Go binary not found: {binary}\n"
            "Run:  go build -o woodoku-solver.exe .   in the project root."
        )
    return subprocess.Popen(
        [binary, "-cv"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,          # line-buffered
    )


def get_proc() -> subprocess.Popen:
    global _proc
    if _proc is None or _proc.poll() is not None:
        _proc = _start()
    return _proc


def solve(
    board: list[list[int]],
    piece_ids: list[int],
) -> list[tuple[int,int,int]] | None:
    """
    Send board + pieces to the solver, return list of (shape_id, row, col)
    or None if the game is over / solver fails.
    """
    proc = get_proc()

    # Build input string
    board_lines = "\n".join(" ".join(str(v) for v in row) for row in board)
    pieces_line = " ".join(str(p) for p in piece_ids)
    payload = board_lines + "\n" + pieces_line + "\n"

    try:
        proc.stdin.write(payload)
        proc.stdin.flush()
    except BrokenPipeError:
        return None

    moves: list[tuple[int,int,int]] = []
    while True:
        line = proc.stdout.readline().strip()
        if not line:
            continue
        if line == "DONE":
            return moves if len(moves) == 3 else None
        if line == "GAME_OVER":
            return None
        parts = line.split()
        if len(parts) == 3:
            moves.append((int(parts[0]), int(parts[1]), int(parts[2])))


def close() -> None:
    global _proc
    if _proc is not None:
        try:
            _proc.stdin.close()
            _proc.wait(timeout=2)
        except Exception:
            _proc.kill()
        _proc = None
