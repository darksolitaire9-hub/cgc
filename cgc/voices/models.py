from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import List, Optional


class LanguageCode(StrEnum):
    """Kokoro language codes (single-letter)."""

    AMERICAN = "a"
    BRITISH = "b"
    JAPANESE = "j"
    CHINESE = "z"
    SPANISH = "e"
    FRENCH = "f"
    HINDI = "h"
    ITALIAN = "i"
    PORTUGUESE_BR = "p"


class Gender(StrEnum):
    FEMALE = "female"
    MALE = "male"


@dataclass(frozen=True)
class VoiceInfo:
    """Metadata for a single Kokoro voice.

    voice_id is the exact engine ID passed to Kokoro (e.g. "af_bella").
    """

    voice_id: str
    lang: LanguageCode
    gender: Gender
    label: str
    traits: str
    target_quality: Optional[str]
    training_minutes: Optional[int]
    overall_grade: Optional[str]
    best_for: List[str]
    recommended: bool = False
