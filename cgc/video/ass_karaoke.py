from __future__ import annotations

from typing import Iterable, List

from cgc.domain.subtitle_chunking import chunk_scene_words
from cgc.domain.subtitles import scene_words
from cgc.domain.types import Story, SubtitleEvent, WordTiming
from cgc.video.subtitle_layout import format_karaoke_sentence


def _scene_word_timings(story: Story) -> dict[int, List[WordTiming]]:
    by_scene: dict[int, List[WordTiming]] = {}
    for scene in story.scenes:
        ws = scene_words(scene)
        if not ws:
            continue
        by_scene[scene.index] = ws
    return by_scene


def build_subtitle_events(story: Story) -> Iterable[SubtitleEvent]:
    events: List[SubtitleEvent] = []
    by_scene = _scene_word_timings(story)

    for scene in story.scenes:
        words = by_scene.get(scene.index)
        if not words:
            continue

        chunks = chunk_scene_words(words)

        for chunk in chunks:
            chunk_words = chunk.words
            if not chunk_words:
                continue

            # Chunk timing: from first word to last word in chunk
            if scene.audio.start is not None and scene.audio.end is not None:
                scene_start = float(scene.audio.start)
                scene_end = float(scene.audio.end)
            else:
                scene_start = min(w.start for w in chunk_words)
                scene_end = max(w.end for w in chunk_words)

            start = max(chunk.start, scene_start)
            end = min(chunk.end, scene_end)

            if end <= start:
                continue

            render = format_karaoke_sentence(chunk_words, start=start, end=end)
            events.append(
                SubtitleEvent(
                    start=start,
                    end=end,
                    text=render.ass,
                )
            )

    events.sort(key=lambda e: e.start)
    return events
