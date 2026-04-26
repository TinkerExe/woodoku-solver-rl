from __future__ import annotations

import numpy as np
import pytest

from woodoku.env.action import ACTION_SPACE_SIZE, encode
from woodoku.env.piece_generator import FixedGenerator, UniformGenerator
from woodoku.env.woodoku_env import WoodokuEnv


def test_reset_returns_valid_obs():
    env = WoodokuEnv()
    obs, _ = env.reset(seed=0)
    assert obs["board"].shape == (9, 9) and obs["board"].sum() == 0
    assert obs["pieces"].shape == (3, 5, 5)
    assert obs["active"].tolist() == [1, 1, 1]
    assert env.action_space.n == ACTION_SPACE_SIZE


def test_action_mask_legal_at_start():
    env = WoodokuEnv(piece_generator=UniformGenerator(seed=42))
    env.reset(seed=42)
    mask = env.action_masks()
    assert mask.dtype == bool
    assert mask.any()
    assert mask.shape == (ACTION_SPACE_SIZE,)


def test_step_illegal_terminates():
    env = WoodokuEnv(piece_generator=FixedGenerator([(100, 100, 100)]))
    env.reset()
    env.step(encode(0, 0, 0))
    _, r, term, _, info = env.step(encode(1, 0, 0))
    assert term and r == 0.0 and info.get("invalid") == "illegal_placement"


def test_full_episode_terminates():
    rng = np.random.default_rng(0)
    env = WoodokuEnv(piece_generator=UniformGenerator(seed=0))
    env.reset(seed=0)
    for _ in range(2000):
        mask = env.action_masks()
        legal = np.flatnonzero(mask)
        a = int(rng.choice(legal))
        _, _, term, trunc, _ = env.step(a)
        if term or trunc:
            return
    pytest.fail("episode did not terminate in 2000 steps")
