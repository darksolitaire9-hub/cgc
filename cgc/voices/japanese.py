from __future__ import annotations

from typing import Tuple

from .models import Gender, LanguageCode, VoiceInfo
from .ratings import GRADE_C, GRADE_C_MINUS, GRADE_C_PLUS

# Japanese: 4F 1M 

VOICE_INFOS: Tuple[VoiceInfo, ...] = (
    VoiceInfo(
        voice_id="jf_alpha",
        lang=LanguageCode.JAPANESE,
        gender=Gender.FEMALE,
        label="Alpha (JP)",
        traits="Japanese female, general-purpose",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C_PLUS,
        best_for=["storytelling", "general"],
        recommended=True,
    ),
    VoiceInfo(
        voice_id="jf_gongitsune",
        lang=LanguageCode.JAPANESE,
        gender=Gender.FEMALE,
        label="Gongitsune",
        traits="Japanese female, fairy-tale corpus (gongitsune)",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["storytelling", "literary"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="jf_nezumi",
        lang=LanguageCode.JAPANESE,
        gender=Gender.FEMALE,
        label="Nezumi",
        traits="Japanese female, short corpus (nezuminoyomeiri)",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C_MINUS,
        best_for=["experimental", "character"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="jf_tebukuro",
        lang=LanguageCode.JAPANESE,
        gender=Gender.FEMALE,
        label="Tebukuro",
        traits="Japanese female, fairy-tale corpus (tebukurowokaini)",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["storytelling"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="jm_kumo",
        lang=LanguageCode.JAPANESE,
        gender=Gender.MALE,
        label="Kumo",
        traits="Japanese male, short corpus (kumonoito)",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C_MINUS,
        best_for=["character", "experimental"],
        recommended=False,
    ),
)
