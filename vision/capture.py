"""
Screen capture — works both on native Windows and inside WSL.

Always captures the FULL primary monitor at its physical pixel resolution
(DPI-aware, so 2K/4K monitors captured correctly).
Board/game area cropping is handled by detector.py via _find_game_area().
"""

from __future__ import annotations
import os
import subprocess
import numpy as np
import cv2


def _is_wsl() -> bool:
    try:
        return "microsoft" in open("/proc/version").read().lower()
    except OSError:
        return False


# ── WSL path: PowerShell DPI-aware full-screen capture ───────────────────────

# SetProcessDPIAware() + GetSystemMetrics gives the real physical pixel count,
# not the DPI-scaled logical size (which would give 1920×1080 on a 2K monitor
# at 150% scaling).
_PS_CAPTURE = r"""
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Cap {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern int  GetSystemMetrics(int n);
    [DllImport("gdi32.dll")]  public static extern int  GetDeviceCaps(IntPtr h, int i);
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
    """Returns (windows_path, linux_path) for a temp PNG."""
    r = subprocess.run(
        ["powershell.exe", "-Command", "[System.IO.Path]::GetTempPath()"],
        capture_output=True, text=True,
    )
    win_temp = r.stdout.strip().rstrip("\\")
    win_path  = win_temp + "\\_woodoku_cap.png"
    linux_r   = subprocess.run(["wslpath", "-u", win_path],
                                capture_output=True, text=True)
    linux_path = linux_r.stdout.strip()
    return win_path, linux_path


def _capture_wsl() -> np.ndarray:
    win_path, linux_path = _wsl_to_win_tmpfile()
    ps = _PS_CAPTURE.replace("{path}", win_path)
    subprocess.run(["powershell.exe", "-Command", ps],
                   capture_output=True, check=True)
    img = cv2.imread(linux_path)
    if img is None:
        raise RuntimeError(f"Screen capture failed — image not found at {linux_path}")
    return img


# ── Windows native path: mss ──────────────────────────────────────────────────

def _capture_native() -> np.ndarray:
    import mss
    with mss.mss() as sct:
        mon = sct.monitors[1]   # primary monitor
        raw = sct.grab(mon)
    return np.array(raw)[:, :, :3]   # BGRA → BGR


# ── public API ────────────────────────────────────────────────────────────────

def get_game_image() -> tuple[np.ndarray, None]:
    """
    Capture the full primary monitor. Returns (BGR image, None).
    The second element is always None — window offset is no longer tracked
    because we capture the whole screen; screen coords == image coords.
    """
    if _is_wsl():
        return _capture_wsl(), None
    return _capture_native(), None
