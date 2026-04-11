from __future__ import annotations

from PIL import Image, ImageDraw

from cgc.config import (
    COLOR_ACCENT_GOLD,
    COLOR_EVAL_BG,
    ZONE_PROGRESS_H,
    ZONE_PROGRESS_Y,
)

FRAME_W = 1080


def draw_progress_bar(frame: Image.Image, progress: float) -> None:
    """
    Draw a horizontal progress strip at ZONE_PROGRESS_Y.

    progress: 0.0 – 1.0  (caller computes audio.start / total_duration)
    """
    draw = ImageDraw.Draw(frame)

    # Track (full width, dim background)
    draw.rectangle(
        [(0, ZONE_PROGRESS_Y), (FRAME_W, ZONE_PROGRESS_Y + ZONE_PROGRESS_H)],
        fill=COLOR_EVAL_BG,
    )

    # Fill (proportional to progress, gold)
    filled_w = int(FRAME_W * max(0.0, min(1.0, progress)))
    if filled_w > 0:
        draw.rectangle(
            [(0, ZONE_PROGRESS_Y), (filled_w, ZONE_PROGRESS_Y + ZONE_PROGRESS_H)],
            fill=COLOR_ACCENT_GOLD,
        )
