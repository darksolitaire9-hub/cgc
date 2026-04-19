from __future__ import annotations

from enum import StrEnum
from typing import Final


class KokoroVoice(StrEnum):
    AF_HEART = "af_heart"
    AF_BELLA = "af_bella"
    AF_NICOLE = "af_nicole"
    AF_KORE = "af_kore"
    AF_AOEDE = "af_aoede"
    AF_SARAH = "af_sarah"
    AF_NOVA = "af_nova"
    AF_ALLOY = "af_alloy"
    AF_JESSICA = "af_jessica"
    AF_RIVER = "af_river"
    AF_SKY = "af_sky"

    AM_FENRIR = "am_fenrir"
    AM_MICHAEL = "am_michael"
    AM_PUCK = "am_puck"
    AM_ECHO = "am_echo"
    AM_ERIC = "am_eric"
    AM_LIAM = "am_liam"
    AM_ONYX = "am_onyx"
    AM_ADAM = "am_adam"

    BF_EMMA = "bf_emma"
    BF_ISABELLA = "bf_isabella"
    BM_GEORGE = "bm_george"
    BM_LEWIS = "bm_lewis"

    JF_ALPHA = "jf_alpha"
    JF_GONGITSUNE = "jf_gongitsune"
    JF_NEZUMI = "jf_nezumi"
    JF_TEbukuro = "jf_tebukuro"
    JM_KUMA = "jm_kuma"

    ZF_XIAOBEI = "zf_xiaobei"
    ZF_XIAONI = "zf_xiaoni"
    ZF_XIAOXIAO = "zf_xiaoxiao"
    ZF_XIAOYI = "zf_xiaoyi"
    ZM_YUNJIAN = "zm_yunjian"
    ZM_YUNXI = "zm_yunxi"
    ZM_YUNXIA = "zm_yunxia"
    ZM_YUNYANG = "zm_yunyang"

    EF_DORA = "ef_dora"
    EM_ALEX = "em_alex"
    EM_SANTA = "em_santa"

    FF_SIWIS = "ff_siwis"

    HF_ALPHA = "hf_alpha"
    HF_BETA = "hf_beta"
    HM_OMEGA = "hm_omega"
    HM_PSI = "hm_psi"

    IF_SARA = "if_sara"
    IM_NICOLA = "im_nicola"

    PF_DORA = "pf_dora"
    PM_ALEX = "pm_alex"
    PM_SANTA = "pm_santa"


VOICE_LABELS: Final[dict[KokoroVoice, str]] = {
    KokoroVoice.AF_HEART: "A - top tier, versatile",
    KokoroVoice.AF_BELLA: "A- - expressive storyteller",
    KokoroVoice.AF_NICOLE: "B- - soft, ASMR-like",
    KokoroVoice.AF_KORE: "C+",
    KokoroVoice.AF_AOEDE: "C+",
    KokoroVoice.AF_SARAH: "C+",
    KokoroVoice.AF_NOVA: "C",
    KokoroVoice.AF_ALLOY: "C",
    KokoroVoice.AF_JESSICA: "D",
    KokoroVoice.AF_RIVER: "D",
    KokoroVoice.AF_SKY: "C-",
    KokoroVoice.AM_FENRIR: "C+ - best male",
    KokoroVoice.AM_MICHAEL: "C+",
    KokoroVoice.AM_PUCK: "C+",
    KokoroVoice.AM_ECHO: "D",
    KokoroVoice.AM_ERIC: "D",
    KokoroVoice.AM_LIAM: "D",
    KokoroVoice.AM_ONYX: "D",
    KokoroVoice.AM_ADAM: "F+",
}


AMERICAN_ENGLISH_VOICES: Final[tuple[KokoroVoice, ...]] = (
    KokoroVoice.AF_HEART,
    KokoroVoice.AF_BELLA,
    KokoroVoice.AF_NICOLE,
    KokoroVoice.AF_KORE,
    KokoroVoice.AF_AOEDE,
    KokoroVoice.AF_SARAH,
    KokoroVoice.AF_NOVA,
    KokoroVoice.AF_ALLOY,
    KokoroVoice.AF_JESSICA,
    KokoroVoice.AF_RIVER,
    KokoroVoice.AF_SKY,
    KokoroVoice.AM_FENRIR,
    KokoroVoice.AM_MICHAEL,
    KokoroVoice.AM_PUCK,
    KokoroVoice.AM_ECHO,
    KokoroVoice.AM_ERIC,
    KokoroVoice.AM_LIAM,
    KokoroVoice.AM_ONYX,
    KokoroVoice.AM_ADAM,
)

RECOMMENDED_AMERICAN_ENGLISH_VOICES: Final[tuple[KokoroVoice, ...]] = (
    KokoroVoice.AF_HEART,
    KokoroVoice.AF_BELLA,
    KokoroVoice.AF_NICOLE,
    KokoroVoice.AF_AOEDE,
    KokoroVoice.AM_FENRIR,
)


def voices_for_lang(lang_code: str) -> tuple[KokoroVoice, ...]:
    if lang_code == "a":
        return AMERICAN_ENGLISH_VOICES
    return tuple()


def voice_label(voice: KokoroVoice | str) -> str:
    if isinstance(voice, str):
        try:
            voice = KokoroVoice(voice)
        except ValueError:
            return "custom"
    return VOICE_LABELS.get(voice, "custom")
