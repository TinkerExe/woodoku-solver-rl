from __future__ import annotations

import numpy as np

from woodoku.env.piece_generator import FixedGenerator
from woodoku.env.reward import legal_moves_norm, line_progress, reward_v1, reward_v2
from woodoku.env.woodoku_env import WoodokuEnv


def test_reward_v1_matches_legacy_formula():
    assert reward_v1(4, 0) == 4.0
    assert reward_v1(3, 5) == 13.0


def test_line_progress_increases_with_more_filled_cells():
    a = np.zeros((9, 9), dtype=np.uint8)
    b = a.copy()
    b[0, :3] = 1
    assert line_progress(b) > line_progress(a)


def test_legal_moves_norm_is_bounded():
    board = np.zeros((9, 9), dtype=np.uint8)
    v = legal_moves_norm(board, (100, 400, 505))
    assert 0.0 <= v <= 1.0


def test_reward_v2_penalizes_terminal_state():
    before = np.zeros((9, 9), dtype=np.uint8)
    after = before.copy()
    r_non_term = reward_v2(
        before_board=before,
        after_board=after,
        n_placed=1,
        n_cleared=0,
        terminated=False,
        remaining_piece_ids_before=(100,),
        remaining_piece_ids_after=(100,),
    )
    r_term = reward_v2(
        before_board=before,
        after_board=after,
        n_placed=1,
        n_cleared=0,
        terminated=True,
        remaining_piece_ids_before=(100,),
        remaining_piece_ids_after=(100,),
    )
    assert r_term < r_non_term


def test_env_reward_v2_differs_from_v1_on_same_move():
    gen = FixedGenerator([(100, 100, 100)])
    env_v1 = WoodokuEnv(piece_generator=gen, reward_version="v1")
    env_v1.reset(seed=0)
    _, r1, _, _, _ = env_v1.step(0)

    gen2 = FixedGenerator([(100, 100, 100)])
    env_v2 = WoodokuEnv(piece_generator=gen2, reward_version="v2")
    env_v2.reset(seed=0)
    _, r2, _, _, _ = env_v2.step(0)

    assert r1 != r2

