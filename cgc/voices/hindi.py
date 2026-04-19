from __future__ import annotations

from typing import Tuple

from .models import Gender, LanguageCode, VoiceInfo
from .ratings import GRADE_C

# Hindi: 2F 2M 

VOICE_INFOS: Tuple[VoiceInfo, ...] = (
    VoiceInfo(
        voice_id="hf_alpha",
        lang=LanguageCode.HINDI,
        gender=Gender.FEMALE,
        label="Alpha (HI)",
        traits="Hindi female, limited training data",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["general"],
        recommended=True,
    ),
    VoiceInfo(
        voice_id="hf_beta",
        lang=LanguageCode.HINDI,
        gender=Gender.FEMALE,
        label="Beta (HI)",
        traits="Hindi female, limited training data",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["general"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="hm_omega",
        lang=LanguageCode.HINDI,
        gender=Gender.MALE,
        label="Omega (HI)",
        traits="Hindi male, limited training data",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["general"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="hm_psi",
        lang=LanguageCode.HINDI,
        gender=Gender.MALE,
        label="Psi (HI)",
        traits="Hindi male, limited training data",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["general"],
        recommended=False,
    ),
)
