from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from cgc.domain.subtitles import build_subtitle_words, scene_words
from cgc.domain.types import Story, WordTiming


@dataclass
class SubtitleEvent:
    start: float
    end: float
    text: str


ASS_GOLD = "&H00D7FF&"  # #FFD700 in ASS BGR format


def _format_sentence(words: List[WordTiming], active_index: int) -> str:
    """
    Build full-sentence ASS text with a single active word highlighted.
    Active word: gold + bold. Others: default style (Montserrat-Bold 88px).
    """
    parts: List[str] = []
    for i, w in enumerate(words):
        token = w.word
        if i == active_index:
            # Highlight active word with colour + bold, then reset (\r)
            parts.append(rf"{{\c{ASS_GOLD}\b1}}{token}{{\r}}")
        else:
            parts.append(token)
    sentence = " ".join(parts)
    # Fixed position: centre of narration zone (x=540, y=1535)
    return r"{\pos(540,1535)}" + sentence


def _scene_word_timings(story: Story) -> dict[int, List[WordTiming]]:
    """
    Group WordTiming objects by scene.index for quick access.
    """
    by_scene: dict[int, List[WordTiming]] = {}
    for scene in story.scenes:
        ws = scene_words(scene)
        if not ws:
            continue
        by_scene[scene.index] = ws
    return by_scene


def build_subtitle_events(story: Story) -> Iterable[SubtitleEvent]:
    r"""
    Build ASS-ready subtitle events.

    - One event per spoken word window.
    - Text contains the full sentence (all words of the scene).
    - The active word (for this event's time window) is highlighted in gold.
    - Position is fixed via \pos to the narration zone centre.
    """
    events: List[SubtitleEvent] = []

    # Pre-group words by scene so we can build full sentences per scene.
    by_scene = _scene_word_timings(story)

    for scene in story.scenes:
        words = by_scene.get(scene.index)
        if not words:
            continue

        for idx, w in enumerate(words):
            text = _format_sentence(words, active_index=idx)
            events.append(
                SubtitleEvent(
                    start=w.start,
                    end=w.end,
                    text=text,
                )
            )

    return events
