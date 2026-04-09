from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

from cgc.config import PipelineConfig
from cgc.domain.types import AudioManifest, SceneAudioRef, Story


def _clip_hash(spoken: str, cfg: PipelineConfig) -> str:
    key = json.dumps(
        {
            "spoken": spoken,
            "voice": cfg.tts.voice,
            "speed": cfg.tts.speed,
            "lang": cfg.tts.lang,
        },
        sort_keys=True,
    )
    return hashlib.sha1(key.encode()).hexdigest()[:16]


def _silence(duration_s: float, sample_rate: int) -> np.ndarray:
    return np.zeros(int(duration_s * sample_rate), dtype=np.float32)


def build_audio_manifest(
    story: Story,
    cfg: PipelineConfig,
) -> AudioManifest:
    """
    Real TTS adapter: generate per-scene clips with Kokoro and return an AudioManifest.
    Does NOT assign timing; only clip_path + duration.
    """
    clips_root = Path(cfg.paths.clips_dir) / story.game_id
    clips_root.mkdir(parents=True, exist_ok=True)

    merged_root = Path(cfg.paths.merged_dir)
    merged_root.mkdir(parents=True, exist_ok=True)

    cache_root = Path(cfg.paths.cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)

    model_path = Path(cfg.tts.model_path)
    voices_path = Path(cfg.tts.voices_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Kokoro model not found: {model_path}")
    if not voices_path.exists():
        raise FileNotFoundError(f"Kokoro voices not found: {voices_path}")

    kokoro = None
    sample_rate = 24000
    merged_clips: list[np.ndarray] = []
    scene_refs: list[SceneAudioRef] = []

    for scene in story.scenes:
        spoken = (scene.spoken_text or "").strip()

        # Empty spoken → short silence to keep timeline continuous
        if not spoken:
            samples = _silence(0.4, sample_rate)
            clip_path = clips_root / f"{scene.index:02d}_{scene.id}.wav"
            sf.write(str(clip_path), samples, sample_rate)
            dur = len(samples) / sample_rate
            scene_refs.append(
                SceneAudioRef(
                    scene_id=scene.id,
                    index=scene.index,
                    clip_path=str(clip_path),
                    duration=dur,
                )
            )
            merged_clips.append(samples)
            continue

        clip_hash = _clip_hash(spoken, cfg)
        cache_file = cache_root / f"{clip_hash}.wav"
        clip_path = clips_root / f"{scene.index:02d}_{scene.id}.wav"

        if cache_file.exists():
            samples, sample_rate = sf.read(str(cache_file), dtype="float32")
        else:
            if kokoro is None:
                kokoro = Kokoro(str(model_path), str(voices_path))

            samples, sample_rate = kokoro.create(
                spoken,
                voice=cfg.tts.voice,
                speed=cfg.tts.speed,
                lang=cfg.tts.lang,
            )
            sf.write(str(cache_file), samples, sample_rate)

        sf.write(str(clip_path), samples, sample_rate)
        dur = len(samples) / sample_rate

        scene_refs.append(
            SceneAudioRef(
                scene_id=scene.id,
                index=scene.index,
                clip_path=str(clip_path),
                duration=dur,
            )
        )
        merged_clips.append(samples)

    merged_audio_path = merged_root / f"{story.game_id}_narration.wav"
    if merged_clips:
        merged = np.concatenate(merged_clips)
        sf.write(str(merged_audio_path), merged, sample_rate)

    return AudioManifest(
        game_id=story.game_id,
        merged_audio_path=str(merged_audio_path),
        scenes=scene_refs,
    )


def build_fake_audio_manifest(
    story: Story,
    cfg: PipelineConfig | None = None,
    *,
    default_seconds: float = 2.0,
) -> AudioManifest:
    """
    Fallback TTS adapter: no real audio, just constant per-scene durations.
    Ignores cfg except for type compatibility.
    """
    scene_refs: list[SceneAudioRef] = []
    for s in story.scenes:
        scene_refs.append(
            SceneAudioRef(
                scene_id=s.id,
                index=s.index,
                clip_path=None,
                duration=default_seconds,
            )
        )

    return AudioManifest(
        game_id=story.game_id,
        merged_audio_path=None,
        scenes=scene_refs,
    )
