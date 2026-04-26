from __future__ import annotations

import time
import traceback

import numpy as np

from woodoku.automation.mouse import place_piece
from woodoku.agent.planner import pick_action_with_rollout
from woodoku.core.rules import apply_move, is_terminal
from woodoku.core.shapes import SHAPE_SIZES
from woodoku.env.action import decode
from woodoku.env.action_masking import action_masks_for, build_agent_obs, build_agent_obs_v2

RETRY_DELAY = 0.35
MAX_FAILURES = 12
SETTLE_AFTER_DRAG = 0.72


def run_rl_screen_loop(
    *,
    model,
    dry_run: bool = False,
    capture_fn,
    find_board_fn,
    read_board_fn,
    find_piece_areas_fn,
    detect_piece_fn,
    obs_version: str = "v1",
    planner: str = "off",
    max_simulations: int = 128,
    max_depth: int = 4,
    time_budget_ms: int = 20,
) -> None:
    """Drive the real game with a MaskablePPO model — no Go solver.

    Keeps a fixed trio (shape ids + active slots) until placements succeed; if the board
    does not change after a drag, the same trio is retried so the agent can choose again.
    """
    consecutive_failures = 0
    trio_ids: list[int | None] = [None, None, None]
    # Start inactive so the first iteration always snapshots a fresh trio from vision.
    active = np.zeros(3, dtype=np.uint8)
    sim_board: np.ndarray | None = None

    def _read_trio_from_vision(img: np.ndarray, board_rect: tuple[int, int, int, int]) -> tuple[list[int | None], list[tuple[int, int, int, int]]]:
        rects = find_piece_areas_fn(img, board_rect)
        ids: list[int | None] = []
        for r in rects:
            ids.append(detect_piece_fn(img, r))
        return ids, rects

    try:
        while True:
            img, off = capture_fn()
            board_rect = find_board_fn(img)
            if board_rect is None:
                consecutive_failures += 1
                if consecutive_failures >= MAX_FAILURES:
                    break
                time.sleep(RETRY_DELAY)
                continue

            board_live = read_board_fn(img, board_rect)
            rects = find_piece_areas_fn(img, board_rect)
            if dry_run:
                if sim_board is None:
                    sim_board = board_live.copy()
                board = sim_board
            else:
                board = board_live

            if not bool(active.any()):
                ids, _ = _read_trio_from_vision(img, board_rect)
                if any(i is None for i in ids):
                    consecutive_failures += 1
                    if consecutive_failures >= MAX_FAILURES:
                        break
                    time.sleep(RETRY_DELAY)
                    continue
                trio_ids = [int(x) for x in ids]
                active[:] = 1
                consecutive_failures = 0
                if dry_run and sim_board is not None and is_terminal(sim_board, tuple(int(x) for x in ids)):
                    sim_board = board_live.copy()
            else:
                for i in range(3):
                    if not active[i] or trio_ids[i] is None:
                        continue
                    det = detect_piece_fn(img, rects[i])
                    if det is not None:
                        trio_ids[i] = int(det)

            if any(trio_ids[i] is None for i in range(3) if active[i]):
                consecutive_failures += 1
                if consecutive_failures >= MAX_FAILURES:
                    break
                time.sleep(RETRY_DELAY)
                continue

            pieces = [int(trio_ids[i]) for i in range(3)]
            obs = build_agent_obs_v2(board, pieces, active) if obs_version == "v2" else build_agent_obs(board, pieces, active)
            mask = action_masks_for(board, pieces, active)
            if not mask.any():
                time.sleep(RETRY_DELAY)
                continue

            if planner == "rollout":
                action = pick_action_with_rollout(
                    model=model,
                    board=board,
                    pieces=pieces,
                    active=active,
                    obs_version=obs_version,
                    max_simulations=max_simulations,
                    max_depth=max_depth,
                    time_budget_ms=time_budget_ms,
                )
            else:
                action, _ = model.predict(obs, action_masks=mask, deterministic=True)
            slot, row, col = decode(int(action))
            if not active[slot]:
                continue

            board_before = board.copy()
            sid = pieces[slot]
            print(f"  action slot={slot} shape={sid} cell=({row},{col}) dry={dry_run}")

            if dry_run:
                assert sim_board is not None
                sim_board, _, _ = apply_move(sim_board, sid, row, col)
                active[slot] = 0
                consecutive_failures = 0
                continue

            place_piece(slot, row, col, rects, board_rect, off, SHAPE_SIZES.get(sid, (1, 1)))
            time.sleep(SETTLE_AFTER_DRAG)

            img2, off2 = capture_fn()
            br2 = find_board_fn(img2)
            if br2 is None:
                continue
            board_after = read_board_fn(img2, br2)
            if np.array_equal(board_before, board_after):
                print("  [warn] board unchanged — placement failed, retrying same trio")
                time.sleep(0.25)
                continue

            active[slot] = 0
            consecutive_failures = 0

    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()


def load_maskable_ppo(path: str):
    from sb3_contrib import MaskablePPO

    return MaskablePPO.load(path)
