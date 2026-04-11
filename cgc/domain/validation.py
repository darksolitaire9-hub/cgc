from __future__ import annotations

from cgc.domain.types import Story


def validate_scene_order(story: Story) -> None:
    """
    Ensure scenes are ordered by index and audio.start is non-decreasing
    where available.
    """
    last_index = -1
    last_start = -1.0

    for scene in story.scenes:
        if scene.index <= last_index:
            raise ValueError("scene indices must be strictly increasing")
        last_index = scene.index

        if scene.audio.start is not None:
            if scene.audio.start < last_start:
                raise ValueError("scene.audio.start must be non-decreasing")
            last_start = scene.audio.start


def validate_scene_durations(story: Story) -> None:
    """
    Ensure each scene's audio duration is positive when start/end are present.
    """
    for scene in story.scenes:
        if scene.audio.start is None or scene.audio.end is None:
            continue
    
            
        if scene.audio.end <= scene.audio.start:
                raise ValueError(
                    f"scene {scene.id!r} has zero or negative duration "
                    f"{scene.audio.end} <= {scene.audio.start}"
                )


def validate_word_windows(story: Story) -> None:
    """
    Ensure each word timing falls within its scene's audio window.
    """
    for scene in story.scenes:
        if scene.audio.start is None or scene.audio.end is None:
            continue

        s_start = scene.audio.start
        s_end = scene.audio.end

        for w in scene.alignment.words:
            if w.start < s_start or w.end > s_end:
                raise ValueError(
                    f"word {w.word!r} in scene {scene.id!r} "
                    f"outside audio window [{s_start}, {s_end}]"
                )
