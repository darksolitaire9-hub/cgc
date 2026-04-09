from __future__ import annotations

from typing import Iterable

from cgc.domain.types import AlignmentManifest, SceneAlignmentRef, Story, WordTiming


def _iter_words(text: str) -> list[str]:
    # Naive split is enough for a fake manifest.
    return [w for w in text.split() if w]


def _evenly_spaced_word_timings(
    words: Iterable[str],
    start: float,
    end: float,
) -> list[WordTiming]:
    words = list(words)
    if not words:
        return []

    total = max(end - start, 0.0)
    if total == 0.0:
        # Degenerate case: all timestamps collapsed to start.
        return [WordTiming(word=w, start=start, end=start) for w in words]

    step = total / len(words)
    timings: list[WordTiming] = []
    cursor = start
    for w in words:
        next_cursor = cursor + step
        timings.append(WordTiming(word=w, start=cursor, end=next_cursor))
        cursor = next_cursor

    return timings


def build_fake_alignment_manifest(story: Story) -> AlignmentManifest:
    """
    Build a fake AlignmentManifest by splitting each scene's spoken_text into
    words and spreading them evenly over the scene's audio duration.

    This assumes audio.start/end have already been assigned by apply_audio_manifest.
    """
    refs: list[SceneAlignmentRef] = []

    for scene in story.scenes:
        # If we don't have audio timing, skip alignment for this scene.
        if scene.audio.start is None or scene.audio.end is None:
            continue

        words = _iter_words(scene.spoken_text)
        timings = _evenly_spaced_word_timings(
            words,
            start=scene.audio.start,
            end=scene.audio.end,
        )

        ref = SceneAlignmentRef(
            scene_id=scene.id,
            index=scene.index,
            words=timings,
        )
        refs.append(ref)

    manifest = AlignmentManifest(
        game_id=story.game_id,
        scenes=refs,
    )
    return manifest
