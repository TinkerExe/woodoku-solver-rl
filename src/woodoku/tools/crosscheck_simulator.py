from __future__ import annotations

import argparse
import os
import random
import subprocess
import sys

import numpy as np

from woodoku.core.rules import apply_move, get_legal_moves_mask
from woodoku.core.shapes import ALL_SHAPE_IDS


def _serialize_board(b: np.ndarray) -> str:
    return "\n".join(" ".join(str(int(v)) for v in row) for row in b)


def _parse_board(lines: list[str]) -> np.ndarray:
    arr = np.array([[int(x) for x in line.split()] for line in lines], dtype=np.uint8)
    assert arr.shape == (9, 9)
    return arr


def _random_board(rng: random.Random, fill_prob: float) -> np.ndarray:
    return np.array([[1 if rng.random() < fill_prob else 0 for _ in range(9)] for _ in range(9)], dtype=np.uint8)


def _pick_legal_move(rng: random.Random, board: np.ndarray):
    sids = list(ALL_SHAPE_IDS)
    rng.shuffle(sids)
    for sid in sids:
        coords = np.argwhere(get_legal_moves_mask(board, sid))
        if len(coords):
            r, c = coords[rng.randrange(len(coords))]
            return sid, int(r), int(c)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--binary", default=os.path.join(os.path.dirname(__file__), "..", "..", "..", "woodoku-solver.exe"))
    args = ap.parse_args()
    binary = os.path.abspath(args.binary)
    if not os.path.exists(binary):
        print(f"Binary not found: {binary}", file=sys.stderr)
        return 1
    proc = subprocess.Popen([binary, "-apply"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
    rng = random.Random(args.seed)
    mismatches = 0
    skipped = 0
    for i in range(args.n):
        b = _random_board(rng, rng.random() * 0.7)
        move = _pick_legal_move(rng, b)
        if move is None:
            skipped += 1
            continue
        sid, r, c = move
        py_new, _, _ = apply_move(b, sid, r, c)
        proc.stdin.write(_serialize_board(b) + "\n")
        proc.stdin.write(f"{sid} {r} {c}\n")
        proc.stdin.flush()
        out_lines = []
        while True:
            line = proc.stdout.readline().rstrip("\n")
            if line == "DONE":
                break
            if line in ("ILLEGAL", "ERR_UNKNOWN_SHAPE"):
                proc.kill()
                return 2
            if line:
                out_lines.append(line)
        go_new = _parse_board(out_lines)
        if not np.array_equal(py_new, go_new):
            mismatches += 1
            if mismatches >= 5:
                break
    proc.stdin.close()
    proc.wait(timeout=2)
    print(f"Ran {args.n} cases, {skipped} skipped")
    print(f"Mismatches: {mismatches}")
    return 0 if mismatches == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
