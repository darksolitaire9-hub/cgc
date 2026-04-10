import os
import warnings
from pathlib import Path

# HF offline — project‑local cache.
# We intentionally force Hugging Face into offline mode so this project
# never makes network calls at runtime. Models are downloaded once into
# .hf_cache during development and then reused from disk.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault(
    "HF_HOME",
    str(Path(__file__).resolve().parent.parent / ".hf_cache"),
)
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# Suppress noisy but harmless upstream torch warnings from Kokoro.
# These come from Kokoro's model definition and PyTorch deprecations
# (single‑layer LSTM dropout, weight_norm). They do not affect runtime
# correctness for this project. If Kokoro or torch is upgraded and these
# warnings change or disappear, this filter block can be revisited.
warnings.filterwarnings("ignore", message=".*dropout option adds dropout.*")
warnings.filterwarnings("ignore", message=".*torch.nn.utils.weight_norm.*")
