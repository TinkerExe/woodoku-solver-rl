from __future__ import annotations

from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from woodoku.agent.planner import pick_action_with_rollout
from woodoku.env.piece_generator import FixedGenerator
from woodoku.env.woodoku_env import WoodokuEnv


def test_obs_v2_has_scalars():
    env = WoodokuEnv(piece_generator=FixedGenerator([(100, 100, 100)]), obs_version="v2")
    obs, _ = env.reset(seed=0)
    assert "scalars" in obs
    assert obs["scalars"].shape == (31,)


def test_planner_returns_legal_action():
    env = ActionMasker(
        WoodokuEnv(piece_generator=FixedGenerator([(100, 100, 100)]), obs_version="v1"),
        lambda e: e.unwrapped.action_masks(),
    )
    obs, _ = env.reset(seed=0)
    mask = env.unwrapped.action_masks()
    # tiny random model for interface compatibility
    model = MaskablePPO("MultiInputPolicy", env, n_steps=32, batch_size=32, verbose=0, seed=0)
    action = pick_action_with_rollout(
        model=model,
        board=env.unwrapped._board,
        pieces=list(env.unwrapped._pieces),
        active=env.unwrapped._active,
        obs_version="v1",
        max_simulations=16,
        max_depth=2,
        time_budget_ms=50,
    )
    assert 0 <= int(action) < 243
    assert bool(mask[int(action)])

