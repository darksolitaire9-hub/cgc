from __future__ import annotations

from .models import Gender, LanguageCode, VoiceInfo
from .names import (
    ESFemale,
    ESMale,
    FRFemale,
    GBFemale,
    GBMale,
    HIFemale,
    HIMale,
    ITFemale,
    ITMale,
    JPFemale,
    JPMale,
    PTBRFemale,
    PTBRMale,
    USFemale,
    USMale,
    ZHFemale,
    ZHMale,
)
from .registry import all_voices


def _voices_for(lang: LanguageCode, gender: Gender | None = None) -> list[VoiceInfo]:
    voices = [v for v in all_voices() if v.lang == lang]
    if gender is not None:
        voices = [v for v in voices if v.gender == gender]
    return voices


def pick_voice(
    *,
    lang: LanguageCode,
    gender: Gender | None = None,
    prefer_recommended: bool = True,
) -> str:
    """Generic dynamic picker by language and optional gender."""
    candidates = _voices_for(lang, gender)
    if not candidates:
        return "af_bella"

    if prefer_recommended:
        rec = [v for v in candidates if v.recommended]
        if rec:
            return rec[0].voice_id

    return candidates[0].voice_id


# --- Enum-based helpers (names → voice_id) ----------------------------------


def pick_us_female(name: USFemale) -> str:
    return name.value


def pick_us_male(name: USMale) -> str:
    return name.value


def pick_gb_female(name: GBFemale) -> str:
    return name.value


def pick_gb_male(name: GBMale) -> str:
    return name.value


def pick_jp_female(name: JPFemale) -> str:
    return name.value


def pick_jp_male(name: JPMale) -> str:
    return name.value


def pick_zh_female(name: ZHFemale) -> str:
    return name.value


def pick_zh_male(name: ZHMale) -> str:
    return name.value


def pick_es_female(name: ESFemale) -> str:
    return name.value


def pick_es_male(name: ESMale) -> str:
    return name.value


def pick_fr_female(name: FRFemale) -> str:
    return name.value


def pick_hi_female(name: HIFemale) -> str:
    return name.value


def pick_hi_male(name: HIMale) -> str:
    return name.value


def pick_it_female(name: ITFemale) -> str:
    return name.value


def pick_it_male(name: ITMale) -> str:
    return name.value


def pick_pt_br_female(name: PTBRFemale) -> str:
    return name.value


def pick_pt_br_male(name: PTBRMale) -> str:
    return name.value
