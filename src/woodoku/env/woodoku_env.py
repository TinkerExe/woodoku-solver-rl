from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from woodoku.core.rules import apply_move, empty_board, get_legal_moves_mask, is_terminal, score_for_move
from woodoku.core.types import BOARD_SIZE, BoardArray, PieceID
from .action import ACTION_SPACE_SIZE, N_SLOTS, decode
from .action_masking import action_masks_for
from .observation import PIECE_OBS_DIM, piece_to_canvas
from .piece_generator import PieceGenerator, UniformGenerator


class WoodokuEnv(gym.Env):
    metadata = {"render_modes": ["ansi"]}

    def __init__(self, piece_generator: PieceGenerator | None = None, render_mode: str | None = None) -> None:
        super().__init__()
        self._gen: PieceGenerator = piece_generator or UniformGenerator()
        self.render_mode = render_mode
        self.observation_space = spaces.Dict(
            {
                "board": spaces.Box(0, 1, (BOARD_SIZE, BOARD_SIZE), dtype=np.uint8),
                "pieces": spaces.Box(0, 1, (N_SLOTS, PIECE_OBS_DIM, PIECE_OBS_DIM), dtype=np.uint8),
                "active": spaces.Box(0, 1, (N_SLOTS,), dtype=np.uint8),
            }
        )
        self.action_space = spaces.Discrete(ACTION_SPACE_SIZE)
        self._board: BoardArray = empty_board()
        self._pieces: list[PieceID] = []
        self._active = np.zeros(N_SLOTS, dtype=np.uint8)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)
        self._gen.reset(seed)
        self._board = empty_board()
        self._draw_new_trio()
        return self._obs(), self._info()

    def step(self, action: int):
        slot, row, col = decode(int(action))
        if not self._active[slot]:
            return self._obs(), 0.0, True, False, self._info(invalid="inactive_slot")
        sid = self._pieces[slot]
        mask = get_legal_moves_mask(self._board, sid)
        if not mask[row, col]:
            return self._obs(), 0.0, True, False, self._info(invalid="illegal_placement")
        self._board, n_placed, n_cleared = apply_move(self._board, sid, row, col)
        self._active[slot] = 0
        reward = score_for_move(n_placed, n_cleared)
        if not self._active.any():
            self._draw_new_trio()
        active_pieces = tuple(self._pieces[i] for i in range(N_SLOTS) if self._active[i])
        terminated = is_terminal(self._board, active_pieces)
        return self._obs(), reward, terminated, False, self._info()

    def action_masks(self) -> np.ndarray:
        return action_masks_for(self._board, self._pieces, self._active)

    def render(self):
        if self.render_mode != "ansi":
            return None
        rows = [" ".join("■" if self._board[r, c] else "·" for c in range(BOARD_SIZE)) for r in range(BOARD_SIZE)]
        rows.append(f"pieces: {self._pieces} active: {self._active.tolist()}")
        return "\n".join(rows)

    def _draw_new_trio(self) -> None:
        self._pieces = list(self._gen.next_three())
        self._active = np.ones(N_SLOTS, dtype=np.uint8)

    def _obs(self):
        pieces = np.stack(
            [
                piece_to_canvas(self._pieces[i]) if self._active[i] else np.zeros((PIECE_OBS_DIM, PIECE_OBS_DIM), dtype=np.uint8)
                for i in range(N_SLOTS)
            ]
        )
        return {"board": self._board.copy(), "pieces": pieces, "active": self._active.copy()}

    def _info(self, **extra):
        return {"pieces": tuple(self._pieces), "active": self._active.copy(), **extra}
