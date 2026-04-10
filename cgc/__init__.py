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

warnings.filterwarnings("ignore", message=".*dropout option adds dropout.*")
warnings.filterwarnings("ignore", message=".*torch.nn.utils.weight_norm.*")
