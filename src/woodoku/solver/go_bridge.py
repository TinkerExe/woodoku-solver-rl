from __future__ import annotations

import os
import subprocess

_BINARY_REL = os.path.join(os.path.dirname(__file__), "..", "..", "..", "woodoku-solver.exe")
_proc: subprocess.Popen | None = None


def _start() -> subprocess.Popen:
    binary = os.path.abspath(_BINARY_REL)
    if not os.path.exists(binary):
        raise FileNotFoundError(
            f"Go binary not found: {binary}\nBuild with: cd go-solver && go build -o ../woodoku-solver.exe ."
        )
    return subprocess.Popen([binary, "-cv"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)


def get_proc() -> subprocess.Popen:
    global _proc
    if _proc is None or _proc.poll() is not None:
        _proc = _start()
    return _proc


def solve(board: list[list[int]], piece_ids: list[int]) -> list[tuple[int, int, int]] | None:
    proc = get_proc()
    payload = "\n".join(" ".join(str(v) for v in row) for row in board) + "\n" + " ".join(str(p) for p in piece_ids) + "\n"
    try:
        proc.stdin.write(payload)
        proc.stdin.flush()
    except BrokenPipeError:
        return None
    moves: list[tuple[int, int, int]] = []
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
