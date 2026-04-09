from __future__ import annotations

from pathlib import Path

from cgc.domain.types import AudioManifest, SceneAudioRef, Story


def build_fake_audio_manifest(
    story: Story,
    *,
    clips_dir: str = "output/fake_clips",
    merged_dir: str = "output/fake_merged",
    default_seconds: float = 2.0,
) -> AudioManifest:
    """
    Stub TTS adapter: no real audio, just pretend each scene has a WAV
    of `default_seconds` duration and a fake merged file path.
    """
    clips_root = Path(clips_dir) / story.game_id
    merged_root = Path(merged_dir)
    merged_root.mkdir(parents=True, exist_ok=True)
    clips_root.mkdir(parents=True, exist_ok=True)

    scene_refs: list[SceneAudioRef] = []
    for s in story.scenes:
        clip_path = clips_root / f"{s.index:02d}_{s.id}.wav"
        # We don't write real audio yet; just declare the path and duration.
        scene_refs.append(
            SceneAudioRef(
                scene_id=s.id,
                index=s.index,
                clip_path=str(clip_path),
                duration=default_seconds,
            )
        )

    merged_audio_path = merged_root / f"{story.game_id}_narration.wav"
    # No real file yet – just a declared path.
    return AudioManifest(
        game_id=story.game_id,
        merged_audio_path=str(merged_audio_path),
        scenes=scene_refs,
    )
