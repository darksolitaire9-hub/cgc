from __future__ import annotations

from pathlib import Path
from typing import Iterable

from cgc.domain.subtitles import SubtitleEvent, escape_ass_text, format_ass_time


def _default_ass_header() -> str:
    # Minimal but valid ASS header with one style. [web:58][web:62]
    return (
        """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,42,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,3,0,2,120,120,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".rstrip()
        + "\n"
    )


def _dialogue_line(event: SubtitleEvent, style: str = "Default") -> str:
    start = format_ass_time(event.start)
    end = format_ass_time(event.end)
    text = escape_ass_text(event.text)
    # Dialogue format per ASS spec. [web:58][web:62]
    return f"Dialogue: 0,{start},{end},{style},,0,0,0,,{text}\n"


def write_ass(
    game_id: str,
    events: Iterable[SubtitleEvent],
    out_dir: str = "output/subtitles",
) -> str:
    """
    Write a minimal ASS subtitle file for the given events and return its path.
    """
    out_path = Path(out_dir) / f"{game_id}.ass"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    header = _default_ass_header()
    lines = [header]

    for ev in events:
        lines.append(_dialogue_line(ev))

    out_path.write_text("".join(lines), encoding="utf-8")
    return str(out_path)
