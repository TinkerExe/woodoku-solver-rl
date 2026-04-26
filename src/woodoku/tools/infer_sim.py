from __future__ import annotations

import argparse

from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from woodoku.agent.planner import pick_action_with_rollout
from woodoku.env.piece_generator import UniformGenerator
from woodoku.env.woodoku_env import WoodokuEnv


def run_infer_sim(
    *,
    model_path: str,
    episodes: int = 3,
    seed_base: int = 0,
    render: bool = False,
    reward_version: str = "v1",
    obs_version: str = "v1",
    planner: str = "off",
    max_simulations: int = 128,
    max_depth: int = 4,
    time_budget_ms: int = 20,
) -> None:
    model = MaskablePPO.load(model_path)
    for ep in range(episodes):
        env = ActionMasker(
            WoodokuEnv(piece_generator=UniformGenerator(seed=seed_base + ep), reward_version=reward_version, obs_version=obs_version),
            lambda e: e.unwrapped.action_masks(),
        )
        obs, _ = env.reset(seed=seed_base + ep)
        ep_r = 0.0
        if render:
            print(env.unwrapped.render())
        while True:
            mask = env.unwrapped.action_masks()
            if planner == "rollout":
                raw = env.unwrapped
                action = pick_action_with_rollout(
                    model=model,
                    board=raw._board,
                    pieces=list(raw._pieces),
                    active=raw._active,
                    obs_version=obs_version,
                    max_simulations=max_simulations,
                    max_depth=max_depth,
                    time_budget_ms=time_budget_ms,
                )
            else:
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
    ap.add_argument("--reward-version", choices=("v1", "v2"), default="v1")
    ap.add_argument("--obs-version", choices=("v1", "v2"), default="v1")
    ap.add_argument("--planner", choices=("off", "rollout"), default="off")
    ap.add_argument("--max-simulations", type=int, default=128)
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--time-budget-ms", type=int, default=20)
    args = ap.parse_args()
    run_infer_sim(
        model_path=args.model,
        episodes=args.episodes,
        seed_base=args.seed_base,
        render=args.render,
        reward_version=args.reward_version,
        obs_version=args.obs_version,
        planner=args.planner,
        max_simulations=args.max_simulations,
        max_depth=args.max_depth,
        time_budget_ms=args.time_budget_ms,
    )


if __name__ == "__main__":
    main()
