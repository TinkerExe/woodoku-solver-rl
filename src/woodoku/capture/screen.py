from __future__ import annotations

import os
import subprocess

import cv2
import numpy as np


def _is_wsl() -> bool:
    try:
        return "microsoft" in open("/proc/version").read().lower()
    except OSError:
        return False


_PS_CAPTURE = r"""
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Cap {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern int  GetSystemMetrics(int n);
}
"@
[Cap]::SetProcessDPIAware() | Out-Null
$sw = [Cap]::GetSystemMetrics(0)
$sh = [Cap]::GetSystemMetrics(1)
$bmp = New-Object System.Drawing.Bitmap($sw, $sh)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new($sw, $sh))
$bmp.Save('{path}')
$g.Dispose()
$bmp.Dispose()
"""


def _wsl_to_win_tmpfile() -> tuple[str, str]:
    r = subprocess.run(["powershell.exe", "-Command", "[System.IO.Path]::GetTempPath()"], capture_output=True, text=True)
    win_temp = r.stdout.strip().rstrip("\\")
    win_path = win_temp + "\\_woodoku_cap.png"
    linux_r = subprocess.run(["wslpath", "-u", win_path], capture_output=True, text=True)
    return win_path, linux_r.stdout.strip()


def _capture_wsl() -> np.ndarray:
    win_path, linux_path = _wsl_to_win_tmpfile()
    subprocess.run(["powershell.exe", "-Command", _PS_CAPTURE.replace("{path}", win_path)], capture_output=True, check=True)
    img = cv2.imread(linux_path)
    if img is None:
        raise RuntimeError(f"Screen capture failed: {linux_path}")
    return img


def _capture_native() -> np.ndarray:
    import mss

    with mss.mss() as sct:
        raw = sct.grab(sct.monitors[1])
    return np.array(raw)[:, :, :3]


def _parse_roi() -> tuple[int, int, int, int] | None:
    # Format: WOODOKU_CAPTURE_ROI="x,y,w,h"
    raw = os.getenv("WOODOKU_CAPTURE_ROI", "").strip()
    if not raw:
        return None
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 4:
        raise ValueError("WOODOKU_CAPTURE_ROI must be 'x,y,w,h'")
    x, y, w, h = (int(p) for p in parts)
    if w <= 0 or h <= 0:
        raise ValueError("WOODOKU_CAPTURE_ROI width/height must be positive")
    return x, y, w, h


def _apply_roi(img: np.ndarray, roi: tuple[int, int, int, int] | None) -> tuple[np.ndarray, tuple[int, int, int, int] | None]:
    if roi is None:
        return img, None
    x, y, w, h = roi
    ih, iw = img.shape[:2]
    x0 = max(0, min(x, iw))
    y0 = max(0, min(y, ih))
    x1 = max(x0, min(x + w, iw))
    y1 = max(y0, min(y + h, ih))
    if x1 <= x0 or y1 <= y0:
        raise ValueError("WOODOKU_CAPTURE_ROI resolves to empty region")
    return img[y0:y1, x0:x1], (x0, y0, x1 - x0, y1 - y0)


def get_game_image() -> tuple[np.ndarray, tuple[int, int, int, int] | None]:
    img = _capture_wsl() if _is_wsl() else _capture_native()
    roi = _parse_roi()
    return _apply_roi(img, roi)
