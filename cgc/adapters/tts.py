from __future__ import annotations

from pathlib import Path

from cgc.config import PipelineConfig
from cgc.domain.types import AudioManifest, SceneAudioRef, Story


def build_fake_audio_manifest(
    story: Story,
    cfg: PipelineConfig,
    default_seconds: float = 2.0,
) -> AudioManifest:
    """
    Build a fake AudioManifest using YAML-provided per-card durations if present,
    falling back to a default duration.

    clip_path format: {audio_root}/clips/{game_id}/{index:02d}_{scene_id}.wav
    """
    base: Path = cfg.game_clip_dir(story.game_id)
    refs: list[SceneAudioRef] = []

    for scene in story.scenes:
        raw = scene.raw or {}
        duration = float(raw.get("duration", default_seconds))

        clip_name = f"{scene.index:02d}_{scene.id}.wav"
        clip_path = str(base / clip_name)

        ref = SceneAudioRef(
            scene_id=scene.id,
            index=scene.index,
            clip_path=clip_path,
            duration=duration,
        )
        refs.append(ref)

    manifest = AudioManifest(
        game_id=story.game_id,
        merged_audio_path=None,
        scenes=refs,
    )
    return manifest


def build_audio_manifest(
    story: Story,
    cfg: PipelineConfig,
) -> AudioManifest:
    """
    Real TTS path (stub for now).

    Intended behavior:
    - For each scene, call Kokoro-ONNX with normalized spoken text and cfg.tts_voice.
    - Save clip into cfg.game_clip_dir(story.game_id).
    - Measure actual duration (e.g., via soundfile) [web:82].
    - Build AudioManifest with real durations and merged_audio_path.
    """
    raise NotImplementedError("real TTS not wired yet")
