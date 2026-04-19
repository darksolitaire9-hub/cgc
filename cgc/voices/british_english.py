from __future__ import annotations

from typing import Tuple

from .models import Gender, LanguageCode, VoiceInfo
from .ratings import GRADE_B_MINUS, GRADE_C, GRADE_C_PLUS, GRADE_D

# British English: 4F 4M 

VOICE_INFOS: Tuple[VoiceInfo, ...] = (
    # Female (bf_*)
    VoiceInfo(
        voice_id="bf_alice",
        lang=LanguageCode.BRITISH,
        gender=Gender.FEMALE,
        label="Alice",
        traits="British female, neutral style",
        target_quality="C",
        training_minutes=None,
        overall_grade=GRADE_D,
        best_for=["experimental", "character"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="bf_emma",
        lang=LanguageCode.BRITISH,
        gender=Gender.FEMALE,
        label="Emma",
        traits="polished British female, likely strongest",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_B_MINUS,
        best_for=["storytelling", "commentary"],
        recommended=True,
    ),
    VoiceInfo(
        voice_id="bf_isabella",
        lang=LanguageCode.BRITISH,
        gender=Gender.FEMALE,
        label="Isabella",
        traits="British female, moderate quality",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["commentary", "short-form"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="bf_lily",
        lang=LanguageCode.BRITISH,
        gender=Gender.FEMALE,
        label="Lily",
        traits="British female, limited data",
        target_quality="C",
        training_minutes=None,
        overall_grade=GRADE_D,
        best_for=["experimental"],
        recommended=False,
    ),
    # Male (bm_*)
    VoiceInfo(
        voice_id="bm_daniel",
        lang=LanguageCode.BRITISH,
        gender=Gender.MALE,
        label="Daniel",
        traits="British male, limited data",
        target_quality="C",
        training_minutes=None,
        overall_grade=GRADE_D,
        best_for=["experimental"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="bm_fable",
        lang=LanguageCode.BRITISH,
        gender=Gender.MALE,
        label="Fable",
        traits="British male, character-friendly",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["character", "storytelling"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="bm_george",
        lang=LanguageCode.BRITISH,
        gender=Gender.MALE,
        label="George",
        traits="British male, moderate quality",
        target_quality="B",
        training_minutes=None,
        overall_grade=GRADE_C,
        best_for=["commentary", "short-form"],
        recommended=False,
    ),
    VoiceInfo(
        voice_id="bm_lewis",
        lang=LanguageCode.BRITISH,
        gender=Gender.MALE,
        label="Lewis",
        traits="British male, more training hours",
        target_quality="C",
        training_minutes=None,
        overall_grade=GRADE_C_PLUS,
        best_for=["commentary", "storytelling"],
        recommended=True,
    ),
)
