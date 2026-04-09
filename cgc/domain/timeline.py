from __future__ import annotations

from dataclasses import replace

from cgc.domain.types import Scene, Story


def assign_scene_timing(story: Story) -> Story:
    """
    For now, treat audio timing as canonical scene timing:
    - scene start = scene.audio.start
    - scene end   = scene.audio.end

    Assumes apply_audio_manifest has already populated audio fields.
    """
    new_scenes: list[Scene] = []

    for scene in story.scenes:
        # If audio is missing, leave as-is for now.
        if scene.audio.start is None or scene.audio.end is None:
            new_scenes.append(scene)
            continue

        # No extra fields to set yet; we just assert that audio timing exists
        # and use it as the canonical scene window.
        new_scenes.append(scene)

    return Story(
        game_id=story.game_id,
        source_url=story.source_url,
        meta=story.meta,
        scenes=new_scenes,
    )


def compute_total_duration(story: Story) -> float:
    """
    Compute total duration as the max audio.end across scenes.
    """
    max_end = 0.0
    for scene in story.scenes:
        end = scene.audio.end
        if end is not None and end > max_end:
            max_end = end
    return max_end


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
        if scene.audio.end < scene.audio.start:
            raise ValueError(
                f"scene {scene.id!r} has negative duration "
                f"{scene.audio.end} < {scene.audio.start}"
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
