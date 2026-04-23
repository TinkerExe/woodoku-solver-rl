"""
Calibration / debug helper.

Run standalone:
    python3 -m vision.calibrate

Saves several debug images:
  calibration_raw.png          — raw captured screenshot
  calibration_cell_mask.png    — pixels matching "empty board cell" colour
  calibration_piece_mask.png   — pixels matching "piece / filled" colour
  calibration_debug.png        — full annotated overlay

Also prints a summary of colour statistics so you can tune thresholds.
"""

from __future__ import annotations
import sys
import os
import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vision.capture  import get_game_image
from vision.detector import (
    find_board, read_board, find_piece_areas, detect_piece_id,
    board_cell_debug_mask, piece_color_debug_mask,
    _find_game_area,
)


def _hsv_stats(img: np.ndarray, mask: np.ndarray) -> str:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    pts = hsv[mask > 0]
    if len(pts) == 0:
        return "no pixels matched"
    return (f"{len(pts)} px  "
            f"H=[{pts[:,0].min()}-{pts[:,0].max()}]  "
            f"S=[{pts[:,1].min()}-{pts[:,1].max()}]  "
            f"V=[{pts[:,2].min()}-{pts[:,2].max()}]")


def annotate_and_save(prefix: str = "calibration") -> None:
    print("Capturing screen …")
    img, window_offset = get_game_image()
    print(f"Captured image size: {img.shape[1]}×{img.shape[0]} px")
    gx, gy, gw, gh = _find_game_area(img)
    print(f"Game area:  x={gx} y={gy} w={gw} h={gh}")

    # ── save raw screenshot ───────────────────────────────────────────────────
    raw_path = f"{prefix}_raw.png"
    cv2.imwrite(raw_path, img)
    print(f"Raw screenshot   → {raw_path}")

    # ── save colour masks ─────────────────────────────────────────────────────
    cell_mask  = board_cell_debug_mask(img)
    piece_mask = piece_color_debug_mask(img)

    cell_vis = cv2.cvtColor(cell_mask, cv2.COLOR_GRAY2BGR)
    cell_vis[cell_mask > 0] = (0, 255, 0)    # green = "board cell" colour
    cv2.imwrite(f"{prefix}_cell_mask.png", cell_vis)

    piece_vis = cv2.cvtColor(piece_mask, cv2.COLOR_GRAY2BGR)
    piece_vis[piece_mask > 0] = (0, 100, 255)  # orange = "piece" colour
    cv2.imwrite(f"{prefix}_piece_mask.png", piece_vis)

    print(f"Cell  mask       → {prefix}_cell_mask.png  ({_hsv_stats(img, cell_mask)})")
    print(f"Piece mask       → {prefix}_piece_mask.png ({_hsv_stats(img, piece_mask)})")

    # ── detect board ──────────────────────────────────────────────────────────
    vis = img.copy()
    board_rect = find_board(img)

    if board_rect is None:
        print("\nERROR: board not detected.")
        print("  → Check calibration_cell_mask.png — the board cells should be white.")
        print("  → If the mask is mostly black, adjust _CELL_HSV_LO/HI in detector.py.")
        cv2.imwrite(f"{prefix}_debug.png", vis)
        return

    bx, by, bw, bh = board_rect
    cv2.rectangle(vis, (bx, by), (bx+bw, by+bh), (0, 255, 0), 3)
    print(f"\nBoard detected:  x={bx} y={by} w={bw} h={bh}")

    cell_w = bw / 9.0
    cell_h = bh / 9.0
    board_state = read_board(img, board_rect)
    filled = sum(v for row in board_state for v in row)
    print(f"Filled cells:    {filled}/81")

    for r in range(9):
        for c in range(9):
            cx = int(bx + (c + 0.5) * cell_w)
            cy = int(by + (r + 0.5) * cell_h)
            colour = (0, 0, 255) if board_state[r][c] else (200, 200, 200)
            cv2.circle(vis, (cx, cy), 4, colour, -1)

    # draw grid lines
    for i in range(10):
        x = int(bx + i * cell_w)
        y = int(by + i * cell_h)
        col = (0, 200, 0) if i % 3 == 0 else (0, 100, 0)
        cv2.line(vis, (x, by), (x, by+bh), col, 1)
        cv2.line(vis, (bx, y), (bx+bw, y), col, 1)

    print("\nDetected board state:")
    for row in board_state:
        print("  " + " ".join("■" if v else "·" for v in row))

    # ── piece areas ───────────────────────────────────────────────────────────
    piece_rects = find_piece_areas(img, board_rect)
    print()
    for i, (px, py, pw, ph) in enumerate(piece_rects):
        cv2.rectangle(vis, (px, py), (px+pw, py+ph), (255, 100, 0), 2)
        shape_id = detect_piece_id(img, (px, py, pw, ph))
        label = str(shape_id) if shape_id is not None else "?"
        cv2.putText(vis, label, (px + 5, py + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        print(f"Piece {i+1}: shape_id = {label}  zone=({px},{py},{pw},{ph})")

        # print blob details for failing pieces
        if shape_id is None:
            crop = img[py:py+ph, px:px+pw]
            raw_mask = piece_color_debug_mask(crop)
            kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            opened  = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel3)
            n, _, stats_b, centroids_b = cv2.connectedComponentsWithStats(opened, connectivity=8)
            print(f"  → {n-1} blobs found:")
            for b in range(1, n):
                a  = stats_b[b, cv2.CC_STAT_AREA]
                bw2= stats_b[b, cv2.CC_STAT_WIDTH]
                bh2= stats_b[b, cv2.CC_STAT_HEIGHT]
                cx2, cy2 = centroids_b[b]
                print(f"     blob{b}: area={a} w={bw2} h={bh2} center=({cx2:.1f},{cy2:.1f})")

    # ── drag source points (where the bot grabs each piece) ──────────────────
    for i, (px, py, pw, ph) in enumerate(piece_rects):
        cx = px + pw // 2
        cy = py + ph // 2
        cv2.circle(vis, (cx, cy), 18, (0, 0, 255), -1)        # red filled dot
        cv2.circle(vis, (cx, cy), 18, (255, 255, 255), 2)     # white outline
        cv2.putText(vis, f"grab{i+1}", (cx - 30, cy - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        print(f"Grab {i+1} screen pos: ({cx}, {cy})")

    out = f"{prefix}_debug.png"
    cv2.imwrite(out, vis)
    print(f"\nAnnotated image  → {out}")


if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else "calibration"
    annotate_and_save(prefix)
