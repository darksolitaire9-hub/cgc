from __future__ import annotations

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
