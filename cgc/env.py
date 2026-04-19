# cgc/env.py
from __future__ import annotations

import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent  # points to cgc/


def setup_hf_cache() -> None:
    """Configure project-local Hugging Face cache.

    HF Hub will:
    - use the cache under cgc/.hf_cache
    - only hit the network when a file is missing.
    """
    hf_home = _ROOT / ".hf_cache"
    os.environ.setdefault("HF_HOME", str(hf_home))
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")


def enable_hf_offline() -> None:
    """Force HF Hub into offline mode (no network)."""
    os.environ["HF_HUB_OFFLINE"] = "1"
