from cgc.config import (
    COLOR_PROGRESS_FILL,
    COLOR_PROGRESS_TRACK,
    ZONE_PROGRESS_H,
    ZONE_PROGRESS_Y,
)

from cgc.video.render_scene import FRAME_W


def build_progress_filter_parts(
    total_duration: float,
    fps: int,
) -> tuple[str, str, str]:
    dur = max(total_duration, 1e-4)

    track_filter = (
        f"drawbox=y={ZONE_PROGRESS_Y}:h={ZONE_PROGRESS_H}:w=iw:"
        f"color=0x{COLOR_PROGRESS_TRACK[0]:02X}"
        f"{COLOR_PROGRESS_TRACK[1]:02X}{COLOR_PROGRESS_TRACK[2]:02X}@1.0:t=fill"
    )

    fill_source = (
        f"color=c=0x{COLOR_PROGRESS_FILL[0]:02X}"
        f"{COLOR_PROGRESS_FILL[1]:02X}{COLOR_PROGRESS_FILL[2]:02X}:"
        f"s={FRAME_W}x{ZONE_PROGRESS_H}:r={fps}:d={dur:.4f}"
    )

    overlay_filter = (
        f"overlay=x='trunc(W*(t/{dur:.4f}))-W':y={ZONE_PROGRESS_Y}:shortest=1"
    )

    return track_filter, fill_source, overlay_filter
