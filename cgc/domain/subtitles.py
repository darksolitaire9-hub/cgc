from __future__ import annotations

from dataclasses import dataclass
from typing import List

from cgc.domain.types import Scene, Story, WordTiming


@dataclass
class SubtitleEvent:
    start: float
    end: float
    text: str
    scene_id: str
    index: int


def scene_words(scene: Scene) -> List[WordTiming]:
    return list(scene.alignment.words)


def _build_word_highlight_text(words: List[WordTiming], active_index: int) -> str:
    """
    Full sentence with the active word highlighted yellow via ASS inline tag.
    {\c&H00FFFF&} = yellow (ASS uses BGR), {\r} resets to style default (white).
    """
    parts: List[str] = []
    for i, w in enumerate(words):
        word = escape_ass_text(w.word)
        if i == active_index:
            parts.append(f"{{\\c&H00FFFF&}}{word}{{\\r}}")
        else:
            parts.append(word)
    return " ".join(parts)


def build_subtitle_events(story: Story) -> List[SubtitleEvent]:
    """
    One SubtitleEvent per word (word-by-word karaoke style).
    Each event shows the full scene sentence with the active word highlighted.
    """
    events: List[SubtitleEvent] = []

    for scene in story.scenes:
        words = scene_words(scene)
        if not words:
            continue
        for i, word in enumerate(words):
            text = _build_word_highlight_text(words, i)
            events.append(
                SubtitleEvent(
                    start=word.start,
                    end=word.end,
                    text=text,
                    scene_id=scene.id,
                    index=scene.index,
                )
            )

    events.sort(key=lambda e: e.start)
    return events


def escape_ass_text(text: str) -> str:
    """Escape literal backslashes and braces for ASS."""
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def format_ass_time(seconds: float) -> str:
    """Format seconds as ASS H:MM:SS.cc timecode."""
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
