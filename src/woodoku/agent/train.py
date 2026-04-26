from __future__ import annotations

import os
from pathlib import Path

from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.callbacks import MaskableEvalCallback
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.callbacks import CallbackList, CheckpointCallback, StopTrainingOnNoModelImprovement
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv

from woodoku.agent.policy import WoodokuFeatures, WoodokuFeaturesV2
from woodoku.env.piece_generator import UniformGenerator
from woodoku.env.woodoku_env import WoodokuEnv


def _make_env(seed: int, monitor_csv: str | None, reward_version: str = "v1", obs_version: str = "v1"):
    def _init():
        env = WoodokuEnv(piece_generator=UniformGenerator(seed=seed), reward_version=reward_version, obs_version=obs_version)
        env = ActionMasker(env, lambda e: e.unwrapped.action_masks())
        # Monitor records episode return/length so TensorBoard gets rollout/ep_* scalars.
        env = Monitor(env, filename=monitor_csv, allow_early_resets=True)
        env.reset(seed=seed)
        return env

    return _init


def train(
    total_timesteps: int = 200_000,
    n_envs: int = 8,
    save_dir: str = "src/woodoku/agent/checkpoints",
    seed: int = 0,
    log_dir: str | None = None,
    checkpoint_freq: int = 50_000,
    eval_freq: int = 25_000,
    eval_episodes: int = 20,
    save_best: bool = False,
    early_stop_patience: int = 0,
    resume_from: str | None = None,
    reward_version: str = "v1",
    obs_version: str = "v1",
    policy_version: str = "v1",
    vec_env_type: str = "dummy",
) -> str:
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    if log_dir is not None:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    monitor_root: str | None = None
    if log_dir is not None:
        monitor_root = os.path.join(log_dir, "monitor")
        Path(monitor_root).mkdir(parents=True, exist_ok=True)
    env_fns = [
        _make_env(
            seed + i,
            os.path.join(monitor_root, f"env-{i}.csv") if monitor_root is not None else None,
            reward_version=reward_version,
            obs_version=obs_version,
        )
        for i in range(n_envs)
    ]
    vec = SubprocVecEnv(env_fns) if vec_env_type == "subproc" else DummyVecEnv(env_fns)

    if resume_from is not None:
        model = MaskablePPO.load(resume_from, env=vec, seed=seed, tensorboard_log=log_dir)
    else:
        extractor_cls = WoodokuFeaturesV2 if policy_version == "v2" else WoodokuFeatures
        model = MaskablePPO(
            "MultiInputPolicy",
            vec,
            policy_kwargs=dict(features_extractor_class=extractor_cls, features_extractor_kwargs=dict(features_dim=256)),
            n_steps=512,
            batch_size=256,
            verbose=1,
            seed=seed,
            tensorboard_log=log_dir,
        )

    callbacks = []
    if checkpoint_freq > 0:
        callbacks.append(
            CheckpointCallback(
                save_freq=checkpoint_freq,
                save_path=save_dir,
                name_prefix=f"ppo_woodoku_seed{seed}_step",
                save_replay_buffer=False,
                save_vecnormalize=False,
            )
        )
    if eval_freq > 0:
        eval_fns = [_make_env(seed + 10_000, None, reward_version=reward_version, obs_version=obs_version)]
        eval_env = SubprocVecEnv(eval_fns) if vec_env_type == "subproc" else DummyVecEnv(eval_fns)
        callback_on_new_best = (
            StopTrainingOnNoModelImprovement(max_no_improvement_evals=early_stop_patience, min_evals=3, verbose=1)
            if early_stop_patience > 0
            else None
        )
        callbacks.append(
            MaskableEvalCallback(
                eval_env=eval_env,
                n_eval_episodes=eval_episodes,
                eval_freq=eval_freq,
                best_model_save_path=save_dir if save_best else None,
                deterministic=True,
                callback_after_eval=callback_on_new_best,
                verbose=1,
            )
        )
    callback = CallbackList(callbacks) if callbacks else None
    model.learn(total_timesteps=total_timesteps, callback=callback)
    out = os.path.join(save_dir, f"ppo_woodoku_seed{seed}.zip")
    model.save(out)
    return out
