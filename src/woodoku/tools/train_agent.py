from __future__ import annotations

import argparse

from woodoku.agent.eval import evaluate
from woodoku.agent.train import train


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--total-timesteps", type=int, default=200_000)
    ap.add_argument("--n-envs", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--eval-episodes", type=int, default=20)
    ap.add_argument("--log-dir", default=None)
    ap.add_argument("--checkpoint-freq", type=int, default=50_000)
    ap.add_argument("--eval-freq", type=int, default=25_000)
    ap.add_argument("--save-best", action="store_true")
    ap.add_argument("--early-stop-patience", type=int, default=0)
    ap.add_argument("--resume-from", default=None)
    ap.add_argument("--save-dir", default="src/woodoku/agent/checkpoints")
    ap.add_argument("--reward-version", choices=("v1", "v2"), default="v1")
    ap.add_argument("--obs-version", choices=("v1", "v2"), default="v1")
    ap.add_argument("--policy-version", choices=("v1", "v2"), default="v1")
    ap.add_argument("--vec-env-type", choices=("dummy", "subproc"), default="dummy")
    args = ap.parse_args()
    out = train(
        total_timesteps=args.total_timesteps,
        n_envs=args.n_envs,
        seed=args.seed,
        log_dir=args.log_dir,
        checkpoint_freq=args.checkpoint_freq,
        eval_freq=args.eval_freq,
        eval_episodes=args.eval_episodes,
        save_best=args.save_best,
        early_stop_patience=args.early_stop_patience,
        resume_from=args.resume_from,
        save_dir=args.save_dir,
        reward_version=args.reward_version,
        obs_version=args.obs_version,
        policy_version=args.policy_version,
        vec_env_type=args.vec_env_type,
    )
    print(f"saved: {out}")
    print(evaluate(out, n_episodes=args.eval_episodes, reward_version=args.reward_version, obs_version=args.obs_version))


if __name__ == "__main__":
    main()
