from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, List, Optional


@dataclass
class SubtitleEvent:
    start: float
    end: float
    text: str


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
    eval_score: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Story:
    game_id: str
    source_url: str
    meta: dict[str, Any]
    scenes: list[Scene] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        # Recursively convert nested dataclasses into JSON‑ready types.
        # This matches the target JSON layout when manifests are applied.
        return asdict(self)


@dataclass
class SceneAudioRef:
    scene_id: str
    index: int
    clip_path: str | None
    duration: float


@dataclass
class AudioManifest:
    game_id: str
    merged_audio_path: str | None
    scenes: list[SceneAudioRef] = field(default_factory=list)


@dataclass
class SceneAlignmentRef:
    scene_id: str
    index: int
    words: list[WordTiming] = field(default_factory=list)


@dataclass
class AlignmentManifest:
    game_id: str
    scenes: list[SceneAlignmentRef] = field(default_factory=list)


@dataclass
class SubtitleChunk:
    start_word_index: int
    end_word_index: int
    words: list[WordTiming] = field(default_factory=list)

    @property
    def start(self) -> float:
        return self.words[0].start if self.words else 0.0

    @property
    def end(self) -> float:
        return self.words[-1].end if self.words else 0.0
