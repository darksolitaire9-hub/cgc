from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PipelineConfig:
    # Base directories
    output_root: Path = Path("output")
    audio_root: Path = Path("audio")  # clips + merged
    subtitles_root: Path = Path("output/subtitles")

    # device
    device: str = "cpu"

    # TTS
    tts_sample_rate: int = 24_000
    tts_clip_dir_name: str = "clips"
    tts_merged_dir_name: str = "merged"
    kokoro_repo_id: str = "hexgrad/Kokoro-82M"
    kokoro_voice: str = "af_nicole"
    kokoro_lang: str = "a"  # American English
    kokoro_speed: float = 1.0  # normal speed

    # Alignment
    alignment_language: str = "en"
    alignment_model_dir: Path = Path(".hf_cache") / "alignment_models"

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


# ── Layout v2 — zone geometry (pixels, 1080×1920 canvas) ──────────────────
ZONE_PLAYER_BAR_Y: int = 200
ZONE_PLAYER_BAR_H: int = 130
ZONE_BOARD_Y: int = 330
ZONE_BOARD_SIZE: int = 1080
FRAME_W: int = 1080
FRAME_H: int = 1920
ZONE_NARRATION_Y: int = 1410
ZONE_NARRATION_H: int = 250
ZONE_PROGRESS_H: int = 10
ZONE_PROGRESS_Y: int = FRAME_H - ZONE_PROGRESS_H  # 1920 - 10 = 1910
SIDE_MARGIN: int = 60
EVAL_STRIP_W: int = 10


# ── Layout v2 — colours (PIL RGB tuples) ──────────────────────────────────
COLOR_BG_PLAYER_BAR = (17, 17, 17)
COLOR_BG_NARRATION = (13, 13, 13)
COLOR_BG_PILL = (28, 28, 28)
COLOR_TEXT_PRIMARY = (255, 255, 255)
COLOR_TEXT_DIM = (136, 136, 136)
COLOR_ACCENT_GOLD = (255, 215, 0)
COLOR_EVAL_WINNING = (79, 195, 247)
COLOR_EVAL_NEUTRAL = (136, 136, 136)
COLOR_EVAL_LOSING = (255, 107, 53)
COLOR_EVAL_BG = (42, 42, 42)


# Progress bar colours (track + fill)
COLOR_PROGRESS_TRACK = COLOR_EVAL_BG
COLOR_PROGRESS_FILL = COLOR_ACCENT_GOLD

# ── Layout v2 — font paths (project-local, portable) ─────────────────────
_FONTS_DIR = Path(__file__).parent / "assets" / "fonts"
FONT_MONTSERRAT_BLACK = _FONTS_DIR / "Montserrat-Black.ttf"  # weight 900
FONT_MONTSERRAT_BOLD = _FONTS_DIR / "Montserrat-Bold.ttf"  # weight 700
FONT_MONTSERRAT_MEDIUM = _FONTS_DIR / "Montserrat-Medium.ttf"  # weight 500

# ── Layout v2 — font sizes (pixels) ───────────────────────────────────────
FONT_SIZE_HOOK: int = 148
FONT_SIZE_SUBTITLE: int = 68
FONT_SIZE_PLAYER: int = 38
FONT_SIZE_RATING: int = 28
FONT_SIZE_BADGE: int = 30
FONT_SIZE_CTA: int = 72

# Subtitle ASS position (center X, Y in pixels on 1080x1920)
ASS_SUBTITLE_X: int = 540
ASS_SUBTITLE_Y: int = 1660
