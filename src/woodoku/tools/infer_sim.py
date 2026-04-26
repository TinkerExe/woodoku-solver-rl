from __future__ import annotations

import argparse

from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from woodoku.env.piece_generator import UniformGenerator
from woodoku.env.woodoku_env import WoodokuEnv


def run_infer_sim(*, model_path: str, episodes: int = 3, seed_base: int = 0, render: bool = False) -> None:
    model = MaskablePPO.load(model_path)
    for ep in range(episodes):
        env = ActionMasker(
            WoodokuEnv(piece_generator=UniformGenerator(seed=seed_base + ep)),
            lambda e: e.unwrapped.action_masks(),
        )
        obs, _ = env.reset(seed=seed_base + ep)
        ep_r = 0.0
        if render:
            print(env.unwrapped.render())
        while True:
            mask = env.unwrapped.action_masks()
            action, _ = model.predict(obs, action_masks=mask, deterministic=True)
            obs, r, term, trunc, _ = env.step(int(action))
            ep_r += float(r)
            if render:
                print(env.unwrapped.render(), f"r={r:.1f}", sep="\n")
            if term or trunc:
                break
        print(f"episode {ep + 1}: total_reward={ep_r:.1f}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run MaskablePPO in the numpy simulator (terminal).")
    ap.add_argument("--model", type=str, required=True)
    ap.add_argument("--episodes", type=int, default=3)
    ap.add_argument("--seed-base", type=int, default=0)
    ap.add_argument("--render", action="store_true", help="Print ascii board after each step")
    args = ap.parse_args()
    run_infer_sim(model_path=args.model, episodes=args.episodes, seed_base=args.seed_base, render=args.render)


if __name__ == "__main__":
    main()
