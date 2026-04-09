from __future__ import annotations

from pathlib import Path

from cgc.domain.types import AudioManifest, SceneAudioRef, Story


def build_fake_audio_manifest(
    story: Story,
    base_dir: str = "s20_narration/clips",
    default_seconds: float = 2.0,
) -> AudioManifest:
    """
    Build a fake AudioManifest using YAML-provided per-card durations if present,
    falling back to a default duration.

    clip_path format: {base_dir}/{game_id}/{index:02d}_{scene_id}.wav
    """
    base = Path(base_dir) / story.game_id

    refs: list[SceneAudioRef] = []
    for scene in story.scenes:
        # Use card's own duration if present in raw, otherwise fallback.
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

    # No merged audio yet; that will come from real TTS later.
    manifest = AudioManifest(
        game_id=story.game_id,
        merged_audio_path=None,
        scenes=refs,
    )
    return manifest
