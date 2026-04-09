from __future__ import annotations

from dataclasses import dataclass

from cgc.domain.types import Story, WordTiming


@dataclass
class SubtitleEvent:
    start: float
    end: float
    text: str


def escape_ass_text(text: str) -> str:
    return text.replace("{", r"\{").replace("}", r"\}")


def build_subtitle_events(story: Story) -> list[SubtitleEvent]:
    events: list[SubtitleEvent] = []
    for scene in story.scenes:
        for w in scene.alignment.words:
            word = w.word.strip()
            if not word:
                continue
            events.append(
                SubtitleEvent(
                    start=w.start,
                    end=w.end,
                    text=word.upper(),
                )
            )
    return events
