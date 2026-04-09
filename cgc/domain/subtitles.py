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
    """
    Return word timings for a scene. For now, this is just the alignment.words list.
    """
    return list(scene.alignment.words)


def _collapse_words_to_text(words: List[WordTiming]) -> str:
    return " ".join(w.word for w in words)


def build_subtitle_events(story: Story) -> List[SubtitleEvent]:
    """
    Build simple per-scene subtitle events using the full word range:
    one event per scene, spanning from first word.start to last word.end.
    """
    events: List[SubtitleEvent] = []

    for scene in story.scenes:
        words = scene_words(scene)
        if not words:
            continue

        start = words[0].start
        end = words[-1].end
        text = _collapse_words_to_text(words)

        events.append(
            SubtitleEvent(
                start=start,
                end=end,
                text=text,
                scene_id=scene.id,
                index=scene.index,
            )
        )

    # Ensure events are sorted by start time
    events.sort(key=lambda e: e.start)
    return events


def escape_ass_text(text: str) -> str:
    """
    Minimal escaping for ASS: escape literal backslashes and braces.
    (ASS uses them for override tags.) [web:58][web:62]
    """
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def format_ass_time(seconds: float) -> str:
    """
    Format seconds as ASS H:MM:SS.cc timecode (centiseconds). [web:58][web:62]
    """
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
