# Woodoku Solver (ML-ready)

## Установка (через uv)

```bash
# Go бинарник в корень репозитория (нужен для cross-check правил, не для игры через RL)
cd go-solver && go build -o ../woodoku-solver.exe . && cd ..

# Python + ML + dev
uv sync --extra ml --extra dev
```

После установки доступна команда `uv run woodoku …` (entry point из `pyproject.toml`).

## Команды (`woodoku` или `python -m woodoku`)

| Режим | Команда | Назначение |
|--------|---------|------------|
| Обучение | `uv run woodoku train [--total-timesteps N] [--n-envs K] [--seed S] [--eval-episodes M] [--log-dir DIR] [--checkpoint-freq C] [--eval-freq E] [--save-best] [--early-stop-patience P] [--resume-from PATH] [--save-dir PATH] [--reward-version {v1,v2}] [--obs-version {v1,v2}] [--policy-version {v1,v2}] [--vec-env-type {dummy,subproc}]` | MaskablePPO, чекпоинты/оценка/ранняя остановка/версии obs/policy |
| Инференс, симулятор | `uv run woodoku infer-sim --model PATH/ppo_....zip [--episodes N] [--seed-base S] [--render] [--reward-version {v1,v2}] [--obs-version {v1,v2}] [--planner {off,rollout}] [--max-simulations K] [--max-depth D] [--time-budget-ms T]` | Политика в `WoodokuEnv` в терминале; optional rollout planner |
| Инференс, игра на экране | `uv run woodoku infer-web --model PATH/ppo_....zip [--dry] [--obs-version {v1,v2}] [--planner {off,rollout}] [--max-simulations K] [--max-depth D] [--time-budget-ms T]` | Захват экрана + drag; optional planner |
| Калибровка CV | `uv run woodoku calibrate [PREFIX]` | `PREFIX_raw.png`, `PREFIX_debug.png`, маски и подписи id/`?` на фигурах |
| Cross-check Python↔Go | `uv run woodoku crosscheck [--n 2000] [--seed 0] [--binary PATH]` | Сверка `apply_move` с `woodoku-solver.exe -apply` |

Эквиваленты через модуль:

- `uv run python -m woodoku …` — то же, что `uv run woodoku …`
- `uv run python -m woodoku.tools.train_agent …` — только обучение (как раньше)
- `uv run python -m woodoku.tools.infer_sim …` — только симулятор
- `uv run python -m woodoku.tools.crosscheck_simulator …` — только cross-check

Старый вход `python -m woodoku.tools.run_bot` теперь требует **`--model …`** и проксирует в `woodoku infer-web` (Go-солвер из бота убран).

### Примеры

```bash
# Быстрый smoke train
uv run woodoku train --total-timesteps 4096 --n-envs 2 --eval-episodes 3

# Train с периодическими чекпоинтами + eval + ранней остановкой
uv run woodoku train --total-timesteps 2000000 --n-envs 8 --log-dir runs/agent-v2 \
  --checkpoint-freq 50000 --eval-freq 25000 --save-best --early-stop-patience 8

# Train с reward v2 (шэйпинг), baseline остаётся v1
uv run woodoku train --total-timesteps 500000 --n-envs 8 --reward-version v2 --log-dir runs/reward-v2

# Train с obs/policy v2 + параллельный сбор в subprocess
uv run woodoku train --total-timesteps 1000000 --n-envs 8 --reward-version v2 --obs-version v2 \
  --policy-version v2 --vec-env-type subproc --log-dir runs/v2-subproc

# Политика в numpy-симуляторе с печатью поля
uv run woodoku infer-sim --model src/woodoku/agent/checkpoints/ppo_woodoku_seed0.zip --episodes 2 --render

# Реальная игра (Windows / BlueStacks и т.п.)
uv run woodoku infer-web --model src/woodoku/agent/checkpoints/ppo_woodoku_seed0.zip

# Проверка распознавания без мыши
uv run woodoku infer-web --model ... --dry

# Инференс в симуляторе с rollout planner (ограничен по бюджету)
uv run woodoku infer-sim --model ... --obs-version v2 --planner rollout --max-simulations 128 --max-depth 4 --time-budget-ms 20
```

После любого изменения `src/woodoku/core/rules.py`:

```bash
uv run woodoku crosscheck --n 5000 --seed 0
```

### TensorBoard из WSL → браузер на Windows

Скаляры вида **`rollout/ep_rew_mean`** / **`rollout/ep_len_mean`** появляются, когда при обучении задан **`--log-dir`**: среды оборачиваются в `Monitor` (см. `agent/train.py`), иначе SB3 часто пишет только `train/*`.

По умолчанию сервис слушает только loopback **внутри** Linux, с хоста страница не откроется.

1. Запускай с привязкой ко всем интерфейсам:

```bash
uv run tensorboard --logdir runs/exp1 --bind_all
```

2. В Chrome/Edge на **Windows** открой: **`http://127.0.0.1:6006`** (или `http://localhost:6006`).

3. Если всё равно пусто: узнай IPv4 WSL. Команда `hostname -I` есть не везде (на Arch без `inetutils` её нет) — тогда, например: `ip -4 -br addr show eth0` или `ip -4 route get 1.1.1.1 | awk '{for(i=1;i<=NF;i++) if($i=="src"){print $(i+1); exit}}'`. На Windows открой `http://ТОТ_IP:6006`.

## Почему на `calibration_*_debug.png` бывает «?»

- **Узкая зона трея**: раньше три прямоугольника не перекрывались — часть фигуры могла оказаться вне своего ROI. Сейчас зоны **шире и перекрываются** (`geometry.py`: `PIECE_SLOT_WIDTH_FRAC`, `PIECE_ZONE_HEIGHT_FRAC`).
- **Две фигуры в одном кропе**: при перекрытии соседний кусок давал лишние blob’ы — добавлены **фильтр по краю ROI**, **closing** маски и **fallback по сетке пикселей** в `detect_piece_id`.
- **HSV**: если тема/яркость другие, подстройте `_PIECE_HSV_*` в `recognition/masks.py`.

Переснимите калибровку: `uv run woodoku calibrate`.

## Логика `infer-web`

- Держим **текущую тройку** `(id слота 0..2)` и **active**, пока все три не поставлены.
- После drag сравниваем доску до/после; если **нет изменений** — ход не принят, **та же тройка**, агент снова выбирает действие.
- Один шаг = **одно** предсказание политики и **один** drag (не пакет из трёх ходов Go).

## Структура

```
go-solver/                  # Go: apply mode для cross-check
src/woodoku/core/           # numpy simulator
src/woodoku/env/            # gymnasium env + masking
src/woodoku/agent/          # train / eval / policy
src/woodoku/recognition/    # CV
src/woodoku/capture/
src/woodoku/automation/
src/woodoku/solver/         # Go bridge (для совместимости модулей, не для infer-web)
src/woodoku/bot/            # rl_screen, legacy loop
src/woodoku/tools/
tests/
```
