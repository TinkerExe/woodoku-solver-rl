# Woodoku Solver (ML-ready)

## Установка (через uv)

```bash
# Go бинарник в корень репозитория
cd go-solver && go build -o ../woodoku-solver.exe . && cd ..

# Python зависимости + dev/ml extras
uv sync --extra ml --extra dev
```

## Запуск

```bash
# dry-run бота (без перетаскивания мышью)
uv run python -m woodoku.tools.run_bot --dry

# калибровка
uv run python -m woodoku.tools.calibrate
```

## ML / RL training

```bash
# smoke-train
uv run python -m woodoku.tools.train_agent --total-timesteps 4096 --n-envs 2 --eval-episodes 3

# после любого изменения core/rules.py обязательно cross-check
uv run python -m woodoku.tools.crosscheck_simulator --n 5000 --seed 0
```

Чекпоинты сохраняются в `src/woodoku/agent/checkpoints/`.

## Структура

```
go-solver/                  # Go solver (unchanged logic + apply mode)
src/woodoku/core/           # numpy simulator
src/woodoku/env/            # gymnasium env + masking
src/woodoku/agent/          # training/eval scaffolding
src/woodoku/recognition/    # CV geometry/masks/classifier
src/woodoku/capture/        # screenshot capture
src/woodoku/automation/     # mouse automation
src/woodoku/solver/         # Go bridge + protocol
src/woodoku/bot/            # bot loop/logging
src/woodoku/tools/          # runnable entrypoints
tests/
```
