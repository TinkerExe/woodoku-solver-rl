from __future__ import annotations

import time

import numpy as np

from woodoku.core.rules import apply_move, is_terminal
from woodoku.env.reward import reward_v1
from woodoku.env.action import decode
from woodoku.env.action_masking import action_masks_for, build_agent_obs, build_agent_obs_v2


def _obs_for(board: np.ndarray, pieces: list[int], active: np.ndarray, obs_version: str) -> dict[str, np.ndarray]:
    return build_agent_obs_v2(board, pieces, active) if obs_version == "v2" else build_agent_obs(board, pieces, active)


def _greedy_rollout_value(
    *,
    model,
    board: np.ndarray,
    pieces: list[int],
    active: np.ndarray,
    obs_version: str,
    depth: int,
) -> float:
    total = 0.0
    b = board.copy()
    a = active.copy()
    for _ in range(max(depth, 0)):
        mask = action_masks_for(b, pieces, a)
        if not mask.any():
            break
        obs = _obs_for(b, pieces, a, obs_version)
        action, _ = model.predict(obs, action_masks=mask, deterministic=True)
        slot, row, col = decode(int(action))
        if not a[slot]:
            break
        sid = pieces[slot]
        if not mask[int(action)]:
            break
        b, n_placed, n_cleared = apply_move(b, sid, row, col)
        total += reward_v1(n_placed, n_cleared)
        a[slot] = 0
        if not a.any():
            break
        remain = tuple(pieces[i] for i in range(3) if a[i])
        if is_terminal(b, remain):
            break
    return float(total)


def pick_action_with_rollout(
    *,
    model,
    board: np.ndarray,
    pieces: list[int],
    active: np.ndarray,
    obs_version: str = "v1",
    max_simulations: int = 128,
    max_depth: int = 4,
    time_budget_ms: int = 20,
) -> int:
    """Select action by one-step expansion + greedy rollout."""
    mask = action_masks_for(board, pieces, active)
    legal = np.flatnonzero(mask)
    if len(legal) == 0:
        return 0

    # Policy-only fallback when search budget is effectively disabled.
    if max_simulations <= 1 or max_depth <= 0 or time_budget_ms <= 0:
        obs = _obs_for(board, pieces, active, obs_version)
        action, _ = model.predict(obs, action_masks=mask, deterministic=True)
        return int(action)

    start = time.perf_counter()
    if len(legal) > max_simulations:
        rng = np.random.default_rng(0)
        candidates = rng.choice(legal, size=max_simulations, replace=False)
    else:
        candidates = legal

    best_action = int(candidates[0])
    best_value = float("-inf")
    for action in candidates:
        if (time.perf_counter() - start) * 1000.0 >= float(time_budget_ms):
            break
        slot, row, col = decode(int(action))
        if not active[slot]:
            continue
        sid = pieces[slot]
        b2, n_placed, n_cleared = apply_move(board, sid, row, col)
        a2 = active.copy()
        a2[slot] = 0
        immediate = reward_v1(n_placed, n_cleared)
        tail = _greedy_rollout_value(
            model=model,
            board=b2,
            pieces=pieces,
            active=a2,
            obs_version=obs_version,
            depth=max_depth - 1,
        )
        value = float(immediate + tail)
        if value > best_value:
            best_value = value
            best_action = int(action)
    return best_action

