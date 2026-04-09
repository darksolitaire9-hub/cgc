from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AudioInfo:
    clip_path: str | None = None
    duration: float | None = None
    start: float | None = None
    end: float | None = None


@dataclass
class WordTiming:
    word: str
    start: float
    end: float


@dataclass
class AlignmentInfo:
    words: list[WordTiming] = field(default_factory=list)


@dataclass
class VisualInfo:
    highlight_mode: str | None = None


@dataclass
class Scene:
    index: int
    id: str
    type: str
    role: str | None = None
    ply: int | None = None
    display_lines: list[str] = field(default_factory=list)
    spoken_text: str = ""
    audio: AudioInfo = field(default_factory=AudioInfo)
    alignment: AlignmentInfo = field(default_factory=AlignmentInfo)
    visual: VisualInfo = field(default_factory=VisualInfo)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Story:
    game_id: str
    source_url: str
    meta: dict[str, Any]
    scenes: list[Scene] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
