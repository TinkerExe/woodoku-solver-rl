from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(prog="woodoku", description="Woodoku RL / vision tools")
    sub = parser.add_subparsers(dest="command", required=True)

    p_train = sub.add_parser("train", help="Train MaskablePPO (same as woodoku.tools.train_agent)")
    p_train.add_argument("--total-timesteps", type=int, default=200_000)
    p_train.add_argument("--n-envs", type=int, default=8)
    p_train.add_argument("--seed", type=int, default=0)
    p_train.add_argument("--eval-episodes", type=int, default=20)
    p_train.add_argument("--log-dir", default=None)
    p_train.add_argument("--checkpoint-freq", type=int, default=50_000)
    p_train.add_argument("--eval-freq", type=int, default=25_000)
    p_train.add_argument("--save-best", action="store_true")
    p_train.add_argument("--early-stop-patience", type=int, default=0)
    p_train.add_argument("--resume-from", default=None)
    p_train.add_argument("--save-dir", default="src/woodoku/agent/checkpoints")
    p_train.add_argument("--reward-version", choices=("v1", "v2"), default="v1")
    p_train.add_argument("--obs-version", choices=("v1", "v2"), default="v1")
    p_train.add_argument("--policy-version", choices=("v1", "v2"), default="v1")
    p_train.add_argument("--vec-env-type", choices=("dummy", "subproc"), default="dummy")

    p_sim = sub.add_parser("infer-sim", help="Run saved policy in gym simulator (terminal)")
    p_sim.add_argument("--model", type=str, required=True)
    p_sim.add_argument("--episodes", type=int, default=3)
    p_sim.add_argument("--seed-base", type=int, default=0)
    p_sim.add_argument("--render", action="store_true")
    p_sim.add_argument("--reward-version", choices=("v1", "v2"), default="v1")
    p_sim.add_argument("--obs-version", choices=("v1", "v2"), default="v1")
    p_sim.add_argument("--planner", choices=("off", "rollout"), default="off")
    p_sim.add_argument("--max-simulations", type=int, default=128)
    p_sim.add_argument("--max-depth", type=int, default=4)
    p_sim.add_argument("--time-budget-ms", type=int, default=20)

    p_web = sub.add_parser("infer-web", help="Run policy on real game via screen capture + mouse")
    p_web.add_argument("--model", type=str, required=True, help="Path to .zip from train")
    p_web.add_argument("--dry", action="store_true", help="No mouse: simulate board with core/rules from first screenshot")
    p_web.add_argument("--obs-version", choices=("v1", "v2"), default="v1")
    p_web.add_argument("--planner", choices=("off", "rollout"), default="off")
    p_web.add_argument("--max-simulations", type=int, default=128)
    p_web.add_argument("--max-depth", type=int, default=4)
    p_web.add_argument("--time-budget-ms", type=int, default=20)

    p_cal = sub.add_parser("calibrate", help="Dump masks and piece-id debug image")
    p_cal.add_argument("prefix", nargs="?", default="calibration", help="Output file prefix")

    p_cross = sub.add_parser("crosscheck", help="Compare Python rules vs Go -apply binary")
    p_cross.add_argument("--n", type=int, default=2000)
    p_cross.add_argument("--seed", type=int, default=0)
    p_cross.add_argument("--binary", default=None)

    args = parser.parse_args()

    if args.command == "train":
        from woodoku.agent.eval import evaluate
        from woodoku.agent.train import train

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
        return

    if args.command == "infer-sim":
        from woodoku.tools.infer_sim import run_infer_sim

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
        return

    if args.command == "infer-web":
        from woodoku.bot.rl_screen import load_maskable_ppo, run_rl_screen_loop
        from woodoku.capture.screen import get_game_image
        from woodoku.recognition.cv_classifier import detect_piece_id, read_board
        from woodoku.recognition.geometry import find_board, find_piece_areas

        model = load_maskable_ppo(args.model)
        run_rl_screen_loop(
            model=model,
            dry_run=args.dry,
            capture_fn=get_game_image,
            find_board_fn=find_board,
            read_board_fn=read_board,
            find_piece_areas_fn=find_piece_areas,
            detect_piece_fn=detect_piece_id,
            obs_version=args.obs_version,
            planner=args.planner,
            max_simulations=args.max_simulations,
            max_depth=args.max_depth,
            time_budget_ms=args.time_budget_ms,
        )
        return

    if args.command == "calibrate":
        from woodoku.tools.calibrate import annotate_and_save

        annotate_and_save(args.prefix)
        return

    if args.command == "crosscheck":
        from woodoku.tools import crosscheck_simulator as cc

        old = sys.argv
        sys.argv = ["crosscheck_simulator", "--n", str(args.n), "--seed", str(args.seed)]
        if args.binary:
            sys.argv += ["--binary", args.binary]
        try:
            code = cc.main()
        finally:
            sys.argv = old
        raise SystemExit(code)


if __name__ == "__main__":
    main()
