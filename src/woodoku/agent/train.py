from __future__ import annotations

import os
from pathlib import Path

from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv

from woodoku.agent.policy import WoodokuFeatures
from woodoku.env.piece_generator import UniformGenerator
from woodoku.env.woodoku_env import WoodokuEnv


def _make_env(seed: int, monitor_csv: str | None):
    def _init():
        env = WoodokuEnv(piece_generator=UniformGenerator(seed=seed))
        env = ActionMasker(env, lambda e: e.unwrapped.action_masks())
        # Monitor records episode return/length so TensorBoard gets rollout/ep_* scalars.
        env = Monitor(env, filename=monitor_csv, allow_early_resets=True)
        env.reset(seed=seed)
        return env

    return _init


def train(total_timesteps: int = 200_000, n_envs: int = 8, save_dir: str = "src/woodoku/agent/checkpoints", seed: int = 0, log_dir: str | None = None) -> str:
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    monitor_root: str | None = None
    if log_dir is not None:
        monitor_root = os.path.join(log_dir, "monitor")
        Path(monitor_root).mkdir(parents=True, exist_ok=True)
    vec = DummyVecEnv(
        [
            _make_env(
                seed + i,
                os.path.join(monitor_root, f"env-{i}.csv") if monitor_root is not None else None,
            )
            for i in range(n_envs)
        ]
    )
    model = MaskablePPO(
        "MultiInputPolicy",
        vec,
        policy_kwargs=dict(features_extractor_class=WoodokuFeatures, features_extractor_kwargs=dict(features_dim=256)),
        n_steps=512,
        batch_size=256,
        verbose=1,
        seed=seed,
        tensorboard_log=log_dir,
    )
    model.learn(total_timesteps=total_timesteps)
    out = os.path.join(save_dir, f"ppo_woodoku_seed{seed}.zip")
    model.save(out)
    return out
