from __future__ import annotations

from typing import Tuple

from .models import Gender, LanguageCode, VoiceInfo

# Brazilian Portuguese: 1F 2M, VOICES.md has only traits + SHA256.

VOICE_INFOS: Tuple[VoiceInfo, ...] = (
    VoiceInfo(
        voice_id="pf_dora",
        lang=LanguageCode.PORTUGUESE_BR,
        gender=Gender.FEMALE,
        label="Dora (PT-BR)",
        traits="Brazilian Portuguese female voice",
        target_quality=None,
        training_minutes=None,
        overall_grade=None,
        best_for=["general"],
        recommended=True,
    ),
    VoiceInfo(
        voice_id="pm_alex",
        lang=LanguageCode.PORTUGUESE_BR,
        gender=Gender.MALE,
        label="Alex (PT-BR)",
        traits="Brazilian Portuguese male voice",
        target_quality=None,
        training_minutes=None,
        overall_grade=None,
        best_for=["general"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="pm_santa",
        lang=LanguageCode.PORTUGUESE_BR,
        gender=Gender.MALE,
        label="Santa (PT-BR)",
        traits="Brazilian Portuguese Santa voice",
        target_quality=None,
        training_minutes=None,
        overall_grade=None,
        best_for=["seasonal", "character"],
        recommended=False,
    ),
)
