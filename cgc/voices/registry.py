from __future__ import annotations

from typing import Dict, Tuple

from .american_english import VOICE_INFOS as _AE
from .brazilian_portuguese import VOICE_INFOS as _PTBR
from .british_english import VOICE_INFOS as _BE
from .french import VOICE_INFOS as _FR
from .hindi import VOICE_INFOS as _HI
from .italian import VOICE_INFOS as _IT
from .japanese import VOICE_INFOS as _JP
from .mandarin_chinese import VOICE_INFOS as _ZH
from .models import LanguageCode, VoiceInfo
from .spanish import VOICE_INFOS as _ES

ALL_VOICE_INFOS: Tuple[VoiceInfo, ...] = (
    *_AE,
    *_BE,
    *_JP,
    *_ZH,
    *_ES,
    *_FR,
    *_HI,
    *_IT,
    *_PTBR,
)

_VOICE_MAP: Dict[str, VoiceInfo] = {info.voice_id: info for info in ALL_VOICE_INFOS}


def all_voices() -> Tuple[VoiceInfo, ...]:
    return ALL_VOICE_INFOS


def voice_info(voice_id: str) -> VoiceInfo | None:
    return _VOICE_MAP.get(voice_id)


def voices_for_lang(lang: LanguageCode) -> Tuple[str, ...]:
    return tuple(info.voice_id for info in ALL_VOICE_INFOS if info.lang == lang)


def recommended_voices_for_lang(lang: LanguageCode) -> Tuple[str, ...]:
    return tuple(
        info.voice_id
        for info in ALL_VOICE_INFOS
        if info.lang == lang and info.recommended
    )
