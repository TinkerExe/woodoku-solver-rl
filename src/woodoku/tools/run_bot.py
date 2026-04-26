from __future__ import annotations

import sys


def main() -> None:
    """Screen agent now uses RL only (Go solver removed from this path)."""
    if "--model" not in sys.argv:
        print(
            "The screen bot uses a trained policy. Example:\n"
            "  uv run woodoku infer-web --model src/woodoku/agent/checkpoints/ppo_woodoku_seed0.zip\n"
            "  uv run woodoku infer-web --model ... --dry   # no mouse, sim board from first screenshot\n",
            file=sys.stderr,
        )
        raise SystemExit(2)
    sys.argv = ["woodoku", "infer-web", *sys.argv[1:]]
    from woodoku.cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
