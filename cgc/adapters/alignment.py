from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

import soundfile as sf
import torch
import whisperx.alignment as wa

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


@dataclass
class AlignmentBackend:
    language: str
    device: str
    cfg: PipelineConfig

    _model: torch.nn.Module | None = None
    _metadata: dict | None = None

    def load(self) -> None:
        """
        Load the WhisperX alignment model for the given language and device,
        using the project-local alignment_model_dir as cache.
        """
        if self._model is not None:
            return

        align_model_dir = self.cfg.alignment_model_dir

        # whisperx.alignment.load_align_model(language_code, device, model_name=None, model_dir=...)
        model, metadata = wa.load_align_model(
            language_code=self.language,
            device=self.device,
            model_name=None,
            model_dir=str(align_model_dir),
        )

        self._model = model
        self._metadata = metadata

    def unload(self) -> None:
        """
        Release the alignment model and clear CUDA cache if applicable.
        """
        self._model = None
        self._metadata = None

        if self.device.startswith("cuda"):
            torch.cuda.empty_cache()

    def _clip_duration_seconds(self, audio_path: str) -> float:
        """
        Compute clip duration in seconds by reading the WAV header only.
        """
        try:
            info = sf.info(audio_path)
            if info.samplerate > 0:
                return float(info.frames) / float(info.samplerate)
        except Exception:
            log.exception(
                "Failed to read audio info for %s; falling back to default duration.",
                audio_path,
            )

        # Fallback: non-zero default to avoid degenerate alignment window
        return 10.0

    def align(
        self,
        *,
        audio_path: str,
        text: str,
        start_offset: float,
    ) -> list[WordTiming]:
        """
        Run forced alignment for a single scene:

        - Build a single WhisperX transcript segment spanning the full clip.
        - Call whisperx.alignment.align(...) with that segment and WAV path.
        - Map result['word_segments'] to WordTiming and apply start_offset.
        """
        if self._model is None or self._metadata is None:
            raise RuntimeError("AlignmentBackend.load() must be called before align().")

        # Compute a realistic segment window based on clip duration.
        clip_duration = self._clip_duration_seconds(audio_path)

        # WhisperX expects an iterable of segments with start/end/text.
        transcript = [
            {
                "start": 0.0,
                "end": clip_duration,
                "text": text,
            }
        ]

        # Run alignment. We pass the audio path so WhisperX loads it internally.
        result = wa.align(
            transcript=transcript,
            model=self._model,
            align_model_metadata=self._metadata,
            audio=audio_path,
            device=self.device,
            interpolate_method="nearest",
            return_char_alignments=False,
            print_progress=False,
            combined_progress=False,
        )

        word_segments = result.get("word_segments", []) or []

        timings: list[WordTiming] = []
        for ws in word_segments:
            word = ws.get("word")
            start = ws.get("start")
            end = ws.get("end")

            if not word:
                continue
            if start is None or end is None:
                continue

            scene_start = start_offset
            scene_end = start_offset + clip_duration

            clamped_start = max(scene_start, start_offset + float(start))
            clamped_end = min(scene_end, start_offset + float(end))

            if clamped_end < clamped_start:
                # Skip pathological cases to avoid negative durations
                continue

            timings.append(
                WordTiming(
                    word=word,
                    start=clamped_start,
                    end=clamped_end,
                )
            )

        # Ensure words are sorted by time for downstream validation/subtitles
        timings.sort(key=lambda w: w.start)
        return timings


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
                    SceneAlignmentRef(scene_id=scene.id, index=scene_index, words=[])
                )
                continue

            clip_path = audio_ref.clip_path
            if not clip_path:
                log.warning(
                    "Audio clip path missing for scene id=%s; skipping alignment for this scene.",
                    scene.id,
                )
                alignment_scenes.append(
                    SceneAlignmentRef(scene_id=scene.id, index=scene_index, words=[])
                )
                continue

            spoken_text = " ".join(scene.display_lines).strip()
            if not spoken_text:
                log.warning(
                    "Empty spoken text for scene id=%s; skipping alignment for this scene.",
                    scene.id,
                )
                alignment_scenes.append(
                    SceneAlignmentRef(scene_id=scene.id, index=scene_index, words=[])
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
                # Programming or configuration error: fail fast, do not recover.
                log.exception(
                    "Programming error while aligning scene id=%s; this is not recoverable.",
                    scene.id,
                )
                raise
            except torch.cuda.OutOfMemoryError:
                # GPU OOM: retry this scene on CPU, then continue.
                log.exception(
                    "CUDA OOM while aligning scene id=%s on device=%s; "
                    "falling back to CPU for this scene.",
                    scene.id,
                    backend.device,
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
                except Exception:
                    log.exception(
                        "CPU alignment also failed for scene id=%s; "
                        "continuing with empty alignment.",
                        scene.id,
                    )
                    words = []
                finally:
                    cpu_backend.unload()
            except Exception:
                # Unexpected data/runtime error: log and continue with empty words.
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
