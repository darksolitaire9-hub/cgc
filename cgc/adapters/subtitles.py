from __future__ import annotations

from pathlib import Path
from typing import Iterable

from cgc.domain.subtitles import SubtitleEvent, format_ass_time


def _default_ass_header() -> str:
    # PlayResX/Y MUST match video dimensions — 1080x1920 portrait.
    # Wrong values cause ffmpeg ass= filter to misplace text.
    # Fontsize 64, MarginV 160 for lower-third on 1920px canvas.
    return """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,64,&H00FFFFFF,&H000000FF,&H00000000,&H96000000,-1,0,0,0,100,100,2,0,1,4,0,2,60,60,160,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _dialogue_line(event: SubtitleEvent, style: str = "Default") -> str:
    start = format_ass_time(event.start)
    end = format_ass_time(event.end)
    # event.text is already ASS-escaped with inline override tags — do NOT re-escape
    return f"Dialogue: 0,{start},{end},{style},,0,0,0,,{event.text}\n"


def write_ass(
    game_id: str,
    events: Iterable[SubtitleEvent],
    out_dir: str = "output/subtitles",
) -> str:
    out_path = Path(out_dir) / f"{game_id}.ass"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [_default_ass_header()]
    for ev in events:
        lines.append(_dialogue_line(ev))

    out_path.write_text("".join(lines), encoding="utf-8")
    return str(out_path)
