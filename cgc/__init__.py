from __future__ import annotations

import os
import warnings
from pathlib import Path

# Use project-local HF cache root
os.environ.setdefault(
    "HF_HOME",
    str(Path(__file__).resolve().parent / ".hf_cache"),
)
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# If Kokoro model is already cached, go fully offline — no update checks.
_hf_cache = Path(__file__).resolve().parent / ".hf_cache"
_kokoro_cache = _hf_cache / "hub" / "models--hexgrad--Kokoro-82M"
if _kokoro_cache.exists():
    os.environ.setdefault("HF_HUB_OFFLINE", "1")

warnings.filterwarnings("ignore", message=".*dropout option adds dropout.*")
warnings.filterwarnings("ignore", message=".*torch.nn.utils.weight_norm.*")
