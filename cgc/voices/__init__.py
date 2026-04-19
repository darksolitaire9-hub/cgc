from __future__ import annotations

from .models import Gender, LanguageCode, VoiceInfo
from .registry import (
    all_voices,
    recommended_voices_for_lang,
    voice_info,
    voices_for_lang,
)

__all__ = [
    "LanguageCode",
    "Gender",
    "VoiceInfo",
    "all_voices",
    "voice_info",
    "voices_for_lang",
    "recommended_voices_for_lang",
    "voice_label",
]


def voice_label(voice_id: str) -> str:
    info = voice_info(voice_id)
    return info.label if info is not None else voice_id
