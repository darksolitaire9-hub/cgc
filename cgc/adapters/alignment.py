from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

import torch

from cgc.config import PipelineConfig
from cgc.domain.types import (
    AlignmentManifest,
    AudioManifest,
    SceneAlignmentRef,
    Story,
    WordTiming,
)

log = logging.getLogger(__name__)


def resolve_device(requested: str) -> str:
    """
    Map user requested device ('cpu' or 'cuda') to an actual torch device string.

    Rules:
    - 'cpu' => 'cpu'
    - 'cuda' => 'cuda' if torch.cuda.is_available() else 'cpu' (with a warning)
    - any other value falls back to 'cpu' with a warning.

    This function does not raise; it always returns a usable device string.
    """
    requested = (requested or "cpu").lower()

    if requested == "cpu":
        return "cpu"

    if requested == "cuda":
        if torch.cuda.is_available():
            return "cuda"
        log.warning(
            "Requested CUDA device, but torch.cuda.is_available() is false; "
            "falling back to CPU."
        )
        return "cpu"

    log.warning("Unknown device '%s'; falling back to CPU.", requested)
    return "cpu"


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


def build_alignment_manifest(
    story: Story,
    audio_manifest: AudioManifest,
    cfg: PipelineConfig,
    *,
    requested_device: str = "cpu",
) -> AlignmentManifest:
    """
    Build a real AlignmentManifest for the given story, using per-scene audio clips.

    This:
    - Resolves actual device ('cpu' or 'cuda') via resolve_device.
    - Loads an AlignmentBackend for cfg.alignment_language.
    - Iterates scenes in story order and uses audio_manifest to find WAV clip paths.
    - Aligns each scene's display text against its audio clip.
    - Returns an AlignmentManifest with absolute word timings.
    """
    device = resolve_device(requested_device)

    backend = AlignmentBackend(
        language=cfg.alignment_language,
        device=device,
        cfg=cfg,
    )

    backend.load()
    try:
        scene_audio_index = {ref.scene_id: ref for ref in audio_manifest.scenes}
        alignment_scenes: list[SceneAlignmentRef] = []

        for scene_index, scene in enumerate(story.scenes):
            audio_ref = scene_audio_index.get(scene.id)
            if audio_ref is None:
                log.warning(
                    "No audio manifest entry for scene id=%s; skipping alignment for this scene.",
                    scene.id,
                )
                alignment_scenes.append(
                    SceneAlignmentRef(
                        scene_id=scene.id,
                        index=scene_index,
                        words=[],
                    )
                )
                continue

            clip_path = audio_ref.clip_path
            if not clip_path:
                log.warning(
                    "Audio clip path missing for scene id=%s; skipping alignment for this scene.",
                    scene.id,
                )
                alignment_scenes.append(
                    SceneAlignmentRef(
                        scene_id=scene.id,
                        index=scene_index,
                        words=[],
                    )
                )
                continue

            spoken_text = " ".join(scene.display_lines).strip()
            if not spoken_text:
                log.warning(
                    "Empty spoken text for scene id=%s; skipping alignment for this scene.",
                    scene.id,
                )
                alignment_scenes.append(
                    SceneAlignmentRef(
                        scene_id=scene.id,
                        index=scene_index,
                        words=[],
                    )
                )
                continue

            start_offset = scene.audio.start or 0.0

            try:
                words = backend.align(
                    audio_path=clip_path,
                    text=spoken_text,
                    start_offset=start_offset,
                )
            except RuntimeError:
                # Programming error (load not called); re-raise to fail loudly.
                raise
            except torch.cuda.OutOfMemoryError:
                log.exception(
                    "CUDA OOM while aligning scene id=%s; falling back to CPU for this scene.",
                    scene.id,
                )
                cpu_backend = AlignmentBackend(
                    language=cfg.alignment_language,
                    device="cpu",
                    cfg=cfg,
                )
                cpu_backend.load()
                try:
                    words = cpu_backend.align(
                        audio_path=clip_path,
                        text=spoken_text,
                        start_offset=start_offset,
                    )
                finally:
                    cpu_backend.unload()
            except Exception:
                log.exception(
                    "Failed to align scene id=%s; continuing with empty alignment.",
                    scene.id,
                )
                words = []

            alignment_scenes.append(
                SceneAlignmentRef(
                    scene_id=scene.id,
                    index=scene_index,
                    words=words,
                )
            )

        return AlignmentManifest(
            game_id=story.game_id,
            scenes=alignment_scenes,
        )
    finally:
        backend.unload()
