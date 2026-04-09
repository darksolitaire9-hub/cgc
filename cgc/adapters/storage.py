from __future__ import annotations

import json
from pathlib import Path

from cgc.domain.types import Story


def save_story(story: Story, out_path: str) -> str:
    """
    Serialize Story as canonical JSON (for sync, debugging, and re-use).
    """
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = story.to_dict()
    text = json.dumps(data, indent=2, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")

    return str(path)
