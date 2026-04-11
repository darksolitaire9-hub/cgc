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

    Design:
    - Full sentence visible for the entire scene audio window (no blinking).
    - Events are chained with no gaps; each event highlights the current word.
    - Pre-word gap [scene_start → first word start]: first word pre-highlighted.
    - Word gap [word_n.start → word_n+1.start]: word_n stays highlighted.
    - Post-word tail [last_word.start → scene_end]: last word stays highlighted.
    """
    events: List[SubtitleEvent] = []

    by_scene = _scene_word_timings(story)

    for scene in story.scenes:
        words = by_scene.get(scene.index)
        if not words:
            continue

        # Determine scene window.
        if scene.audio.start is not None and scene.audio.end is not None:
            scene_start = float(scene.audio.start)
            scene_end = float(scene.audio.end)
        else:
            scene_start = min(w.start for w in words)
            scene_end = max(w.end for w in words)

        if scene_end <= scene_start:
            continue

        n = len(words)

        # Optional leading gap: scene_start → first word start.
        if words[0].start > scene_start:
            text = _format_sentence(words, active_index=0)
            events.append(
                SubtitleEvent(
                    start=scene_start,
                    end=words[0].start,
                    text=text,
                )
            )

        # One event per word: word_n.start → word_n+1.start (or scene_end for last).
        for idx, w in enumerate(words):
            ev_start = w.start
            ev_end = words[idx + 1].start if idx < n - 1 else scene_end

            # Clamp to scene window.
            ev_start = max(ev_start, scene_start)
            ev_end = min(ev_end, scene_end)

            if ev_end <= ev_start:
                continue

            text = _format_sentence(words, active_index=idx)
            events.append(SubtitleEvent(start=ev_start, end=ev_end, text=text))

    events.sort(key=lambda e: e.start)
    return events
