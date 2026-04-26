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
    args = ap.parse_args()
    out = train(total_timesteps=args.total_timesteps, n_envs=args.n_envs, seed=args.seed, log_dir=args.log_dir)
    print(f"saved: {out}")
    print(evaluate(out, n_episodes=args.eval_episodes))


if __name__ == "__main__":
    main()
