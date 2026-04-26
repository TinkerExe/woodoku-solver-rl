from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from woodoku.core.rules import apply_move, empty_board, get_legal_moves_mask, is_terminal
from woodoku.core.types import BOARD_SIZE, BoardArray, PieceID
from .action import ACTION_SPACE_SIZE, N_SLOTS, decode
from .action_masking import action_masks_for
from .observation import PIECE_OBS_DIM, SCALARS_DIM, board_scalars, piece_to_canvas
from .piece_generator import PieceGenerator, UniformGenerator
from .reward import reward_v1, reward_v2


class WoodokuEnv(gym.Env):
    metadata = {"render_modes": ["ansi"]}

    def __init__(
        self,
        piece_generator: PieceGenerator | None = None,
        render_mode: str | None = None,
        reward_version: str = "v1",
        obs_version: str = "v1",
    ) -> None:
        super().__init__()
        self._gen: PieceGenerator = piece_generator or UniformGenerator()
        self.render_mode = render_mode
        if reward_version not in ("v1", "v2"):
            raise ValueError(f"unsupported reward_version: {reward_version}")
        self.reward_version = reward_version
        if obs_version not in ("v1", "v2"):
            raise ValueError(f"unsupported obs_version: {obs_version}")
        self.obs_version = obs_version
        obs_dict: dict[str, spaces.Space] = {
            "board": spaces.Box(0, 1, (BOARD_SIZE, BOARD_SIZE), dtype=np.uint8),
            "pieces": spaces.Box(0, 1, (N_SLOTS, PIECE_OBS_DIM, PIECE_OBS_DIM), dtype=np.uint8),
            "active": spaces.Box(0, 1, (N_SLOTS,), dtype=np.uint8),
        }
        if self.obs_version == "v2":
            obs_dict["scalars"] = spaces.Box(0.0, 1.0, (SCALARS_DIM,), dtype=np.float32)
        self.observation_space = spaces.Dict(obs_dict)
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
        board_before = self._board.copy()
        remaining_before = tuple(self._pieces[i] for i in range(N_SLOTS) if self._active[i] and i != slot)
        self._board, n_placed, n_cleared = apply_move(self._board, sid, row, col)
        self._active[slot] = 0
        remaining_after = tuple(self._pieces[i] for i in range(N_SLOTS) if self._active[i])
        if not self._active.any():
            self._draw_new_trio()
        active_pieces = tuple(self._pieces[i] for i in range(N_SLOTS) if self._active[i])
        terminated = is_terminal(self._board, active_pieces)
        if self.reward_version == "v2":
            reward = reward_v2(
                before_board=board_before,
                after_board=self._board,
                n_placed=n_placed,
                n_cleared=n_cleared,
                terminated=terminated,
                remaining_piece_ids_before=remaining_before,
                remaining_piece_ids_after=remaining_after,
            )
        else:
            reward = reward_v1(n_placed, n_cleared)
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
        out: dict[str, np.ndarray] = {"board": self._board.copy(), "pieces": pieces, "active": self._active.copy()}
        if self.obs_version == "v2":
            out["scalars"] = board_scalars(self._board, self._pieces, self._active)
        return out

    def _info(self, **extra):
        return {"pieces": tuple(self._pieces), "active": self._active.copy(), **extra}
