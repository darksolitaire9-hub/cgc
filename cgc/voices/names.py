from __future__ import annotations

from enum import StrEnum


class USFemale(StrEnum):
    HEART = "af_heart"
    ALLOY = "af_alloy"
    AOEDE = "af_aoede"
    BELLA = "af_bella"
    JESSICA = "af_jessica"
    KORE = "af_kore"
    NICOLE = "af_nicole"
    NOVA = "af_nova"
    RIVER = "af_river"
    SARAH = "af_sarah"
    SKY = "af_sky"


class USMale(StrEnum):
    ADAM = "am_adam"
    ECHO = "am_echo"
    ERIC = "am_eric"
    FENRIR = "am_fenrir"
    LIAM = "am_liam"
    MICHAEL = "am_michael"
    ONYX = "am_onyx"
    PUCK = "am_puck"
    SANTA = "am_santa"


class GBFemale(StrEnum):
    ALICE = "bf_alice"
    EMMA = "bf_emma"
    ISABELLA = "bf_isabella"
    LILY = "bf_lily"


class GBMale(StrEnum):
    DANIEL = "bm_daniel"
    FABLE = "bm_fable"
    GEORGE = "bm_george"
    LEWIS = "bm_lewis"


class JPFemale(StrEnum):
    ALPHA = "jf_alpha"
    GONGITSUNE = "jf_gongitsune"
    NEZUMI = "jf_nezumi"
    TEBUKURO = "jf_tebukuro"


class JPMale(StrEnum):
    KUMO = "jm_kumo"


class ZHFemale(StrEnum):
    XIAOBEI = "zf_xiaobei"
    XIAONI = "zf_xiaoni"
    XIAOXIAO = "zf_xiaoxiao"
    XIAOYI = "zf_xiaoyi"


class ZHMale(StrEnum):
    YUNJIAN = "zm_yunjian"
    YUNXI = "zm_yunxi"
    YUNXIA = "zm_yunxia"
    YUNYANG = "zm_yunyang"


class ESFemale(StrEnum):
    DORA = "ef_dora"


class ESMale(StrEnum):
    ALEX = "em_alex"
    SANTA = "em_santa"


class FRFemale(StrEnum):
    SIWIS = "ff_siwis"


class HIFemale(StrEnum):
    ALPHA = "hf_alpha"
    BETA = "hf_beta"


class HIMale(StrEnum):
    OMEGA = "hm_omega"
    PSI = "hm_psi"


class ITFemale(StrEnum):
    SARA = "if_sara"


class ITMale(StrEnum):
    NICOLA = "im_nicola"


class PTBRFemale(StrEnum):
    DORA = "pf_dora"


class PTBRMale(StrEnum):
    ALEX = "pm_alex"
    SANTA = "pm_santa"
