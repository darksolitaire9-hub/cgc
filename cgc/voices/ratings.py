from __future__ import annotations

from typing import Dict

GRADE_A = "A"
GRADE_A_MINUS = "A-"
GRADE_B_MINUS = "B-"
GRADE_C_PLUS = "C+"
GRADE_C = "C"
GRADE_C_MINUS = "C-"
GRADE_D = "D"
GRADE_F_PLUS = "F+"

GRADE_EXPLANATIONS: Dict[str, str] = {
    GRADE_A: "High-quality training data with strong coverage.",
    GRADE_A_MINUS: "High-quality data with slightly less coverage than A.",
    GRADE_B_MINUS: "Moderate-quality data or less coverage.",
    GRADE_C_PLUS: "Decent data but limited or uneven coverage.",
    GRADE_C: "Lower training data quality or quantity.",
    GRADE_C_MINUS: "Notable limitations; best for stylized use.",
    GRADE_D: "Minimal or noisy data; experimental.",
    GRADE_F_PLUS: "Very limited/problematic data; experimental only.",
}
