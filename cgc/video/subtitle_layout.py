from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from cgc.config import FRAME_W, ZONE_NARRATION_H, ZONE_NARRATION_Y
from cgc.domain.types import WordTiming

_ASS_GOLD = "&H00D7FF&"


@dataclass(frozen=True)
class RenderResult:
    ass: str
    debug: Optional[dict] = None


_SUBTITLE_X: int = FRAME_W // 2
_SUBTITLE_Y: int = ZONE_NARRATION_Y + ZONE_NARRATION_H - 30


def _escape_ass(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace("{", r"\{").replace("}", r"\}")
    return text


def format_karaoke_sentence(
    words: List[WordTiming],
    start: float,
    end: float,
    debug: bool = False,
) -> RenderResult:
    """
    Build a single ASS line with \k karaoke timings.
    Renderer will highlight words in order as time progresses.
    """
    if not words or end <= start:
        return RenderResult(ass="")

    # Normalize times relative to chunk start
    base = start
    total_duration = max(end - base, 0.001)

    # Compute per-word durations in seconds based on alignment
    durations_sec: List[float] = []
    for w in words:
        dur = max(w.end - w.start, 0.001)
        durations_sec.append(dur)

    # Scale durations to fit exactly into [0, total_duration]
    sum_dur = sum(durations_sec)
    if sum_dur <= 0:
        dur_cs = [int(total_duration * 100)] + [0] * (len(words) - 1)
    else:
        scale = total_duration / sum_dur
        dur_cs = [max(1, int(d * scale * 100)) for d in durations_sec]

    # Build \k segments
    parts: List[str] = []
    for idx, (w, k) in enumerate(zip(words, dur_cs)):
        token = _escape_ass(w.word)
        # Assumes style has karaoke colors; we just set timing
        parts.append(rf"{{\k{k}}}{token}")

        if idx != len(words) - 1:
            parts.append(" ")

    body = "".join(parts)

    ass = rf"{{\pos({_SUBTITLE_X},{_SUBTITLE_Y})}}{{\c{_ASS_GOLD}}}{body}"

    dbg = None
    if debug:
        dbg = {
            "start": start,
            "end": end,
            "word_count": len(words),
            "dur_cs": dur_cs,
            "tokens": [w.word for w in words],
        }

    return RenderResult(ass=ass, debug=dbg)
