from __future__ import annotations

import warnings

# Only keep warning filters here.
warnings.filterwarnings("ignore", message=".*dropout option adds dropout.*")
warnings.filterwarnings("ignore", message=".*torch.nn.utils.weight_norm.*")
