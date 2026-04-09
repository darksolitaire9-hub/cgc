from __future__ import annotations

from pathlib import Path

from cgc.domain.subtitles import SubtitleEvent, escape_ass_text


def _fmt(t: float) -> str:
    if t < 0:
        t = 0.0
    cs = int(round(t * 100))
    s, cs = divmod(cs, 100)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _header(w: int = 1080, h: int = 1920, margin_v: int = 540) -> str:
    return (
        f"[Script Info]\n"
        f"PlayResX: {w}\n"
        f"PlayResY: {h}\n"
        f"WrapStyle: 2\n"
        f"ScaledBorderAndShadow: yes\n"
        f"\n"
        f"[V4+ Styles]\n"
        f"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        f"OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        f"ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        f"Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: TikTokMain,Inter,74,"
        f"&H00FFFFFF,"  # white
        f"&H00000000,"  # unused
        f"&H00000000,"  # outline
        f"&H00000000,"  # back
        f"-1,0,0,0,"  # bold, italic, underline, strikeout
        f"100,100,0,0,"
        f"1,5,0,"
        f"2,"
        f"40,40,{margin_v},1\n"
        f"\n"
        f"[Events]\n"
        f"Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )


def write_ass(
    game_id: str,
    events: list[SubtitleEvent],
    out_dir: str = "output/subtitles",
    *,
    width: int = 1080,
    height: int = 1920,
    margin_v: int = 540,
) -> str:
    lines: list[str] = [_header(w=width, h=height, margin_v=margin_v)]

    for ev in events:
        text = escape_ass_text(ev.text)
        lines.append(
            f"Dialogue: 0,{_fmt(ev.start)},{_fmt(ev.end)},TikTokMain,,0,0,0,,{text}"
        )

    path = Path(out_dir) / f"{game_id}.ass"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)
