from __future__ import annotations

from PIL import Image, ImageDraw

_THICKNESS = 14  # thicker bar for social video
_BAR_COLOR = (0, 255, 255)  # cyan — matches ASS karaoke highlight
_TRACK_COLOR = (30, 30, 30)  # near-black track (full perimeter, always drawn)


def draw_progress_bar(
    img: Image.Image,
    *,
    current_time: float,
    total_duration: float,
    thickness: int = _THICKNESS,
    bar_color: tuple[int, int, int] = _BAR_COLOR,
    track_color: tuple[int, int, int] = _TRACK_COLOR,
) -> Image.Image:
    """
    Draw a perimeter progress tracer that travels clockwise around the frame.

    Path: top-left → top-right → bottom-right → bottom-left → top-left.

    current_time is the global time in seconds since video start.
    """
    if total_duration <= 0:
        return img

    w, h = img.size
    draw = ImageDraw.Draw(img)
    t = thickness

    segments: list[tuple[tuple[float, float], tuple[float, float], float]] = [
        ((0, 0), (w, 0), w),  # top:    left  → right
        ((w, 0), (w, h), h),  # right:  top   → bottom
        ((w, h), (0, h), w),  # bottom: right → left
        ((0, h), (0, 0), h),  # left:   bottom → top
    ]

    perimeter = 2 * w + 2 * h

    # Draw full track
    for (x1, y1), (x2, y2), _ in segments:
        draw.line([(x1, y1), (x2, y2)], fill=track_color, width=t)

    # Draw elapsed portion
    progress = min(max(current_time / total_duration, 0.0), 1.0)
    remaining = progress * perimeter

    for (x1, y1), (x2, y2), length in segments:
        if remaining <= 0:
            break
        fill_len = min(remaining, length)
        frac = fill_len / length
        ex = x1 + frac * (x2 - x1)
        ey = y1 + frac * (y2 - y1)
        draw.line([(x1, y1), (ex, ey)], fill=bar_color, width=t)
        remaining -= fill_len

    return img
