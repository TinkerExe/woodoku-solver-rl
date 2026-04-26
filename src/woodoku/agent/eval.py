from __future__ import annotations

import numpy as np
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from woodoku.env.piece_generator import UniformGenerator
from woodoku.env.woodoku_env import WoodokuEnv


def evaluate(
    model_path: str,
    n_episodes: int = 50,
    seed_base: int = 1000,
    reward_version: str = "v1",
    obs_version: str = "v1",
) -> dict:
    model = MaskablePPO.load(model_path)
    rewards, lengths = [], []
    for ep in range(n_episodes):
        env = ActionMasker(
            WoodokuEnv(
                piece_generator=UniformGenerator(seed=seed_base + ep),
                reward_version=reward_version,
                obs_version=obs_version,
            ),
            lambda e: e.unwrapped.action_masks(),
        )
        obs, _ = env.reset(seed=seed_base + ep)
        ep_r, ep_len = 0.0, 0
        while True:
            mask = env.unwrapped.action_masks()
            action, _ = model.predict(obs, action_masks=mask, deterministic=True)
            obs, r, term, trunc, _ = env.step(int(action))
            ep_r += r
            ep_len += 1
            if term or trunc:
                break
        rewards.append(ep_r)
        lengths.append(ep_len)
    return {"mean_reward": float(np.mean(rewards)), "std_reward": float(np.std(rewards)), "mean_length": float(np.mean(lengths)), "n": n_episodes}
