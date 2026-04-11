# cgc/video/progress.py
from cgc.video.render_scene import FRAME_W

BAR_Y = 1880
BAR_H = 24
_BAR_TRACK = "#2A2A2A"
_BAR_FILL = "#FFD700"


def build_progress_filter_parts(total_duration: float) -> tuple[str, str, str]:
    """
    Returns (track_filter, fill_source, overlay_filter) for -filter_complex.

    Wire them up as:
        [in]{track_filter}[track];
        {fill_source}[fill];
        [track][fill]{overlay_filter}[out]
    """
    dur = max(total_duration, 1e-4)

    # Static grey track — drawbox is fine here; no per-frame t needed
    track_filter = f"drawbox=y={BAR_Y}:h={BAR_H}:w=iw:color={_BAR_TRACK}@1.0:t=fill"

    # Full-width gold bar as a virtual colour source
    fill_source = f"color=c={_BAR_FILL}:s={FRAME_W}x{BAR_H}:d={dur:.4f}"

    # overlay evaluates x PER FRAME — t is the real PTS here
    # Slides a full-width bar from x=-W to x=0 over [0, dur]
    overlay_filter = f"overlay=x='trunc(W*(t/{dur:.4f}))-W':y={BAR_Y}:shortest=1"

    return track_filter, fill_source, overlay_filter
