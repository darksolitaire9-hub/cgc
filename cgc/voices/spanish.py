from __future__ import annotations

from typing import Tuple

from .models import Gender, LanguageCode, VoiceInfo

# Spanish: 1F 2M, VOICES.md has no grade/duration for these
VOICE_INFOS: Tuple[VoiceInfo, ...] = (
    VoiceInfo(
        voice_id="ef_dora",
        lang=LanguageCode.SPANISH,
        gender=Gender.FEMALE,
        label="Dora (ES)",
        traits="Spanish female voice",
        target_quality=None,
        training_minutes=None,
        overall_grade=None,
        best_for=["experimental"],
        recommended=True,
    ),
    VoiceInfo(
        voice_id="em_alex",
        lang=LanguageCode.SPANISH,
        gender=Gender.MALE,
        label="Alex (ES)",
        traits="Spanish male voice",
        target_quality=None,
        training_minutes=None,
        overall_grade=None,
        best_for=["experimental"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="em_santa",
        lang=LanguageCode.SPANISH,
        gender=Gender.MALE,
        label="Santa (ES)",
        traits="Spanish male Santa voice",
        target_quality=None,
        training_minutes=None,
        overall_grade=None,
        best_for=["seasonal", "character"],
        recommended=False,
    ),
)
