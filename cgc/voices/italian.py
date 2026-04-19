from __future__ import annotations

from typing import Tuple

from .models import Gender, LanguageCode, VoiceInfo
from .ratings import GRADE_C

# Italian: 1F 1M

VOICE_INFOS: Tuple[VoiceInfo, ...] = (
    VoiceInfo(
        voice_id="if_sara",
        lang=LanguageCode.ITALIAN,
        gender=Gender.FEMALE,
        label="Sara (IT)",
        traits="Italian female voice",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["general"],
        recommended=True,
    ),
    VoiceInfo(
        voice_id="im_nicola",
        lang=LanguageCode.ITALIAN,
        gender=Gender.MALE,
        label="Nicola (IT)",
        traits="Italian male voice",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["general"],
        recommended=False,
    ),
)
