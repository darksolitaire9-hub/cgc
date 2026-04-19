from __future__ import annotations

from typing import Tuple

from .models import Gender, LanguageCode, VoiceInfo
from .ratings import GRADE_B_MINUS

# French: 1F 

VOICE_INFOS: Tuple[VoiceInfo, ...] = (
    VoiceInfo(
        voice_id="ff_siwis",
        lang=LanguageCode.FRENCH,
        gender=Gender.FEMALE,
        label="Siwis",
        traits="French female voice (SIWIS corpus)",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_B_MINUS,
        best_for=["storytelling", "general"],
        recommended=True,
    ),
)
