from __future__ import annotations

from pathlib import Path
from typing import Iterable

from cgc.config import FONT_SIZE_SUBTITLE
from cgc.video.ass_karaoke import SubtitleEvent


def _default_ass_header() -> str:
    return f"""\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

Style: Default,Montserrat-Bold,{FONT_SIZE_SUBTITLE},&H00FFFFFF,&H000000FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,4,2,2,40,40,320,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def format_ass_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    total_centis = int(round(seconds * 100))
    centis = total_centis % 100
    total_seconds = total_centis // 100
    s = total_seconds % 60
    total_minutes = total_seconds // 60
    m = total_minutes % 60
    h = total_minutes // 60
    return f"{h:d}:{m:02d}:{s:02d}.{centis:02d}"


def _dialogue_line(event: SubtitleEvent, style: str = "Default") -> str:
    start = format_ass_time(event.start)
    end = format_ass_time(event.end)
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
