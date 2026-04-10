# cgc/domain/subtitles.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from cgc.domain.types import Scene, Story, WordTiming


@dataclass
class SubtitleWord:
    scene_id: str
    scene_index: int
    word: str
    start: float
    end: float


def scene_words(scene: Scene) -> List[WordTiming]:
    return list(scene.alignment.words)


def build_subtitle_words(story: Story) -> List[SubtitleWord]:
    """
    Domain-level representation: each spoken word with its scene and timing.
    No ASS tags, no styles, just data.
    """
    items: List[SubtitleWord] = []
    for scene in story.scenes:
        words = scene_words(scene)
        for w in words:
            items.append(
                SubtitleWord(
                    scene_id=scene.id,
                    scene_index=scene.index,
                    word=w.word,
                    start=w.start,
                    end=w.end,
                )
            )
    items.sort(key=lambda w: w.start)
    return items
