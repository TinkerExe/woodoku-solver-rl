from __future__ import annotations

import sys

import cv2

from woodoku.capture.screen import get_game_image
from woodoku.recognition.cv_classifier import detect_piece_id, read_board
from woodoku.recognition.geometry import _find_game_area, find_board, find_piece_areas
from woodoku.recognition.masks import board_cell_debug_mask, piece_color_debug_mask


def annotate_and_save(prefix: str = "calibration") -> None:
    img, _ = get_game_image()
    gx, gy, gw, gh = _find_game_area(img)
    raw_path = f"{prefix}_raw.png"
    cv2.imwrite(raw_path, img)
    cv2.imwrite(f"{prefix}_cell_mask.png", board_cell_debug_mask(img))
    cv2.imwrite(f"{prefix}_piece_mask.png", piece_color_debug_mask(img))
    vis = img.copy()
    board_rect = find_board(img)
    if board_rect is None:
        cv2.imwrite(f"{prefix}_debug.png", vis)
        return
    bx, by, bw, bh = board_rect
    cv2.rectangle(vis, (bx, by), (bx + bw, by + bh), (0, 255, 0), 3)
    _ = read_board(img, board_rect)
    for i, (px, py, pw, ph) in enumerate(find_piece_areas(img, board_rect)):
        cv2.rectangle(vis, (px, py), (px + pw, py + ph), (255, 100, 0), 2)
        sid = detect_piece_id(img, (px, py, pw, ph))
        cv2.putText(vis, str(sid) if sid is not None else "?", (px + 5, py + 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
    cv2.imwrite(f"{prefix}_debug.png", vis)
    print(f"game area: {gx},{gy},{gw},{gh}")


if __name__ == "__main__":
    annotate_and_save(sys.argv[1] if len(sys.argv) > 1 else "calibration")
