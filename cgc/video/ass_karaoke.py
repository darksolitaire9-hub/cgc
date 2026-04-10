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


def escape_ass_text(text: str) -> str:
    """Escape literal backslashes and braces for ASS."""
    return (
        text.replace("\\", "\\\\")  # single backslash → double
        .replace("{", r"\{")
        .replace("}", r"\}")
    )


def build_subtitle_events(story: Story) -> List[SubtitleEvent]:
    """
    One SubtitleEvent per word, showing only that word.
    No full sentence, no colour tags.
    """
    events: List[SubtitleEvent] = []

    for scene in story.scenes:
        words = scene_words(scene)
        if not words:
            continue

        for w in words:
            text = escape_ass_text(w.word)
            events.append(
                SubtitleEvent(
                    start=w.start,
                    end=w.end,
                    text=text,
                    scene_id=scene.id,
                    index=scene.index,
                )
            )

    events.sort(key=lambda e: e.start)
    return events
