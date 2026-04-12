from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

from cgc.config import PipelineConfig
from cgc.domain.types import AudioManifest, SceneAudioRef, Story


def normalize_spoken_text(text: str) -> str:
    text = " ".join(text.split())
    if text and text[-1] not in ".!?":
        text += "."
    return text


def _make_kokoro_pipeline(cfg: PipelineConfig) -> KPipeline:
    device = getattr(cfg, "device", "cpu")
    print(
        f"[tts] constructing Kokoro KPipeline: repo_id=hexgrad/Kokoro-82M "
        f"lang={cfg.kokoro_lang!r} device={device!r}"
    )
    pipeline = KPipeline(
        lang_code=cfg.kokoro_lang,
        repo_id="hexgrad/Kokoro-82M",
        device=device,  # ← was missing
    )
    print(f"[tts] KPipeline constructed: {pipeline!r}")
    return pipeline


def build_audio_manifest(story: Story, cfg: PipelineConfig) -> AudioManifest:
    """
    Real TTS using Kokoro KPipeline (af_nicole).

    Clips:
        audio/clips/{game_id}/{index}_{scene.id}.wav

    Merged:
        audio/merged/{game_id}.wav
    """

    sample_rate = cfg.tts_sample_rate
    clips_dir = cfg.game_clip_dir(story.game_id)
    clips_dir.mkdir(parents=True, exist_ok=True)
    cfg.merged_audio_dir.mkdir(parents=True, exist_ok=True)

    pipeline = _make_kokoro_pipeline(cfg)

    scene_refs: list[SceneAudioRef] = []

    for scene in story.scenes:
        raw_text = " ".join(scene.display_lines) if scene.display_lines else ""
        text = normalize_spoken_text(raw_text)

        clip_path = clips_dir / f"{scene.index:02d}_{scene.id}.wav"

        chunks: list[np.ndarray] = []
        for _, _, audio in pipeline(
            text, voice=cfg.kokoro_voice, speed=cfg.kokoro_speed
        ):
            chunks.append(audio)

        if not chunks:
            raise RuntimeError(
                f"Kokoro produced no audio for scene {scene.id!r} (text={text!r})"
            )

        samples = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
        sf.write(str(clip_path), samples, sample_rate)

        duration = len(samples) / sample_rate
        scene_refs.append(
            SceneAudioRef(
                scene_id=scene.id,
                index=scene.index,
                clip_path=str(clip_path),
                duration=duration,
            )
        )
        print(f"  [tts] {scene.id} → {duration:.2f}s  ({clip_path.name})")

    merged_path = cfg.game_merged_audio_path(story.game_id)
    _write_merged_audio(scene_refs, merged_path, sample_rate)

    return AudioManifest(
        game_id=story.game_id,
        merged_audio_path=str(merged_path),
        scenes=scene_refs,
    )


def _write_merged_audio(
    scenes: list[SceneAudioRef],
    out_path: Path,
    sample_rate: int,
) -> None:
    """Concatenate all clip WAVs into a single merged WAV in scene order."""
    merged: list[np.ndarray] = []
    # Ensure order by index
    for ref in sorted(scenes, key=lambda s: s.index):
        if ref.clip_path is None:
            continue
        data, sr = sf.read(ref.clip_path, dtype="float32")
        if sr != sample_rate:
            raise RuntimeError(
                f"Sample rate mismatch in {ref.clip_path}: expected {sample_rate}, got {sr}"
            )
        merged.append(data)
    sf.write(str(out_path), np.concatenate(merged), sample_rate)
    print(f"  [tts] merged → {out_path}")


def build_fake_audio_manifest(
    story: Story,
    cfg: PipelineConfig,
    default_seconds: float = 2.0,
) -> AudioManifest:
    """Return a manifest with fake durations and no audio paths."""
    scene_refs = [
        SceneAudioRef(
            scene_id=scene.id,
            index=scene.index,
            clip_path=None,
            duration=default_seconds,
        )
        for scene in story.scenes
    ]
    return AudioManifest(
        game_id=story.game_id,
        merged_audio_path=None,
        scenes=scene_refs,
    )
