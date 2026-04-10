from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PipelineConfig:
    # Base directories
    output_root: Path = Path("output")
    audio_root: Path = Path("s20_narration")  # clips + merged
    subtitles_root: Path = Path("output/subtitles")

    # TTS
    tts_voice: str = "cinematic-bullet"
    tts_sample_rate: int = 24000
    tts_clip_dir_name: str = "clips"
    tts_merged_dir_name: str = "merged"

    # Alignment
    alignment_language: str = "en"

    @property
    def clips_dir(self) -> Path:
        return self.audio_root / self.tts_clip_dir_name

    @property
    def merged_audio_dir(self) -> Path:
        return self.audio_root / self.tts_merged_dir_name

    def game_clip_dir(self, game_id: str) -> Path:
        return self.clips_dir / game_id

    def game_merged_audio_path(self, game_id: str) -> Path:
        return self.merged_audio_dir / f"{game_id}.wav"