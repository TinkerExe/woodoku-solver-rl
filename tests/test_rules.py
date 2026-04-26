from __future__ import annotations

import numpy as np
import pytest

from woodoku.core.rules import _check_and_clear, apply_move, empty_board, get_legal_moves_mask, is_terminal
from woodoku.core.shapes import ALL_SHAPE_IDS


def test_empty_board_all_legal_for_single_cell():
    assert get_legal_moves_mask(empty_board(), 100).sum() == 81


def test_apply_move_places_correctly():
    b = empty_board()
    new, placed, cleared = apply_move(b, 400, 0, 0)
    assert placed == 4 and cleared == 0
    assert new[0, 0] == 1 and new[1, 1] == 1 and new[2, 2] == 0


def test_clear_intersection_counted_once():
    b = empty_board()
    b[0, :] = 1
    b[:, 0] = 1
    _, n = _check_and_clear(b)
    assert n == 17


def test_illegal_move_raises():
    b = empty_board()
    b[0, 0] = 1
    with pytest.raises(ValueError):
        apply_move(b, 100, 0, 0)


def test_terminal_when_all_pieces_unplaceable():
    b = np.ones((9, 9), dtype=np.uint8)
    b[4, 4] = 0
    assert not is_terminal(b, (100,))
    assert is_terminal(b, (400,))


def test_legal_mask_shape_and_dtype():
    b = empty_board()
    for sid in ALL_SHAPE_IDS[:10]:
        m = get_legal_moves_mask(b, sid)
        assert m.shape == (9, 9)
        assert m.dtype == bool
