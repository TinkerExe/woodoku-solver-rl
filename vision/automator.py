"""
Click / drag automation.

On native Windows: uses pyautogui.
On WSL:           calls powershell.exe with Win32 mouse_event API.
"""

from __future__ import annotations
import os
import subprocess
import time


DELAY_BETWEEN_PIECES = 0.40   # seconds after each placed piece
DELAY_AFTER_SET      = 1.10   # seconds after all 3 pieces (clear animation)
DRAG_DURATION_MS     = 400    # drag speed in milliseconds


def _is_wsl() -> bool:
    return "microsoft" in open("/proc/version").read().lower() if os.path.exists("/proc/version") else False


# ── coordinate helpers ────────────────────────────────────────────────────────

def _board_cell_screen(
    row: float, col: float,
    board_rect: tuple[int,int,int,int],
    window_offset: tuple[int,int,int,int] | None,
) -> tuple[int, int]:
    bx, by, bw, bh = board_rect
    cell_w, cell_h = bw / 9.0, bh / 9.0
    ix = bx + (col + 0.5) * cell_w
    iy = by + (row + 0.5) * cell_h
    if window_offset:
        ix += window_offset[0]
        iy += window_offset[1]
    return int(ix), int(iy)


def _piece_center_screen(
    piece_rect: tuple[int,int,int,int],
    window_offset: tuple[int,int,int,int] | None,
) -> tuple[int, int]:
    px, py, pw, ph = piece_rect
    ix = px + pw / 2.0
    iy = py + ph / 2.0
    if window_offset:
        ix += window_offset[0]
        iy += window_offset[1]
    return int(ix), int(iy)


# ── WSL drag via PowerShell ───────────────────────────────────────────────────

_PS_DRAG_TEMPLATE = r"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class M {{
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, UIntPtr e);
    public const uint DOWN = 0x0002, UP = 0x0004, MOVE = 0x0001, ABS = 0x8000;
}}
"@
[M]::SetProcessDPIAware() | Out-Null
[M]::SetCursorPos({fx}, {fy})
Start-Sleep -Milliseconds 80
[M]::mouse_event([M]::DOWN, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 120
$steps = 20
for ($i = 1; $i -le $steps; $i++) {{
    $x = {fx} + ($i * ({tx} - {fx}) / $steps)
    $y = {fy} + ($i * ({ty} - {fy}) / $steps)
    [M]::SetCursorPos([int]$x, [int]$y)
    Start-Sleep -Milliseconds {step_ms}
}}
[M]::SetCursorPos({tx}, {ty})
Start-Sleep -Milliseconds 60
[M]::mouse_event([M]::UP, 0, 0, 0, [UIntPtr]::Zero)
"""


def _drag_wsl(fx: int, fy: int, tx: int, ty: int) -> None:
    step_ms = max(1, DRAG_DURATION_MS // 20)
    ps = _PS_DRAG_TEMPLATE.format(fx=fx, fy=fy, tx=tx, ty=ty, step_ms=step_ms)
    subprocess.run(["powershell.exe", "-Command", ps], capture_output=True)


# ── native drag via pyautogui ─────────────────────────────────────────────────

def _drag_native(fx: int, fy: int, tx: int, ty: int) -> None:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.moveTo(fx, fy, duration=0.1)
    time.sleep(0.05)
    pyautogui.mouseDown(button="left")
    time.sleep(0.10)
    pyautogui.moveTo(tx, ty, duration=DRAG_DURATION_MS / 1000.0)
    time.sleep(0.05)
    pyautogui.mouseUp(button="left")


def _drag(fx: int, fy: int, tx: int, ty: int) -> None:
    if _is_wsl():
        _drag_wsl(fx, fy, tx, ty)
    else:
        _drag_native(fx, fy, tx, ty)


# ── public API ────────────────────────────────────────────────────────────────

def place_piece(
    piece_idx: int,
    shape_id: int,
    move_row: int,
    move_col: int,
    piece_rects: list[tuple[int,int,int,int]],
    board_rect: tuple[int,int,int,int],
    window_offset: tuple[int,int,int,int] | None,
    shape_size: tuple[int,int],
) -> None:
    fx, fy = _piece_center_screen(piece_rects[piece_idx], window_offset)

    ph, pw = shape_size
    # Y: cursor must be 1 cell below the piece's bottom EDGE
    # bottom edge of piece = move_row + ph (in cell units)
    # 1 cell below that edge = move_row + ph + 1 cell = row centre move_row + ph + 0.5
    target_row = move_row + ph + 0.5
    # X: piece is centred on cursor
    target_col = move_col + (pw - 1) / 2.0
    tx, ty = _board_cell_screen(target_row, target_col, board_rect, window_offset)

    print(f"  drag ({fx},{fy}) → ({tx},{ty})")
    _drag(fx, fy, tx, ty)
    time.sleep(DELAY_BETWEEN_PIECES)


def execute_moves(
    moves: list[tuple[int,int,int]],
    piece_ids: list[int],
    piece_rects: list[tuple[int,int,int,int]],
    board_rect: tuple[int,int,int,int],
    window_offset: tuple[int,int,int,int] | None,
    shape_sizes: dict[int, tuple[int,int]],
) -> None:
    available = {i: sid for i, sid in enumerate(piece_ids)}
    for shape_id, row, col in moves:
        idx = next((i for i, sid in available.items() if sid == shape_id), None)
        if idx is None:
            print(f"  [warn] shape {shape_id} not found in available pieces {available}")
            continue
        del available[idx]
        size = shape_sizes.get(shape_id, (1, 1))
        place_piece(idx, shape_id, row, col, piece_rects, board_rect, window_offset, size)
    time.sleep(DELAY_AFTER_SET)
