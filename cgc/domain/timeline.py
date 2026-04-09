from __future__ import annotations

from dataclasses import replace

from cgc.domain.types import Scene, Story


def with_default_durations(story: Story, *, default_seconds: float = 2.0) -> Story:
    """Return a new Story where scenes without duration get a default."""
    scenes: list[Scene] = []
    for s in story.scenes:
        audio = s.audio
        dur = audio.duration if audio.duration is not None else default_seconds
        audio2 = replace(audio, duration=dur)
        scenes.append(replace(s, audio=audio2))
    return replace(story, scenes=scenes)


def assign_scene_timing(story: Story) -> Story:
    """Return a new Story with audio.start/end filled from durations."""
    cursor = 0.0
    scenes: list[Scene] = []

    for s in story.scenes:
        audio = s.audio
        dur = audio.duration or 0.0
        start = cursor
        end = cursor + dur
        cursor = end
        scenes.append(
            replace(
                s,
                audio=replace(audio, start=start, end=end, duration=dur),
            )
        )

    return replace(story, scenes=scenes)


def compute_total_duration(story: Story) -> float:
    last_end = 0.0
    for s in story.scenes:
        if s.audio.end is None:
            continue
        last_end = max(last_end, float(s.audio.end))
    return last_end
