from __future__ import annotations

from typing import List

from cgc.domain.types import SubtitleChunk, WordTiming

# Tunable policy
MAX_WORDS = 8  # soft target
HARD_MAX_WORDS = 10  # absolute ceiling
GAP_THRESHOLD = 0.60  # seconds
MIN_WORDS_FOR_COMMA_BREAK = 4

_HARD_PUNCT = (".", "!", "?")
_SOFT_PUNCT = (",", ";")


def _ends_with(token: str, endings: tuple[str, ...]) -> bool:
    return any(token.endswith(e) for e in endings)


def chunk_scene_words(words: List[WordTiming]) -> List[SubtitleChunk]:
    """
    Split a scene's words into subtitle chunks based on:
      - hard punctuation (.!?)
      - soft punctuation (,) when chunk is long enough
      - timing gaps >= GAP_THRESHOLD
      - max words per chunk

    Pure domain logic — no ASS, no pixels.
    """
    if not words:
        return []

    chunks: List[SubtitleChunk] = []
    current: List[WordTiming] = []
    current_start_idx = 0

    def flush_chunk(start_idx: int, end_idx: int, items: List[WordTiming]) -> None:
        if not items:
            return
        chunks.append(
            SubtitleChunk(
                start_word_index=start_idx,
                end_word_index=end_idx,
                words=list(items),
            )
        )

    for i, w in enumerate(words):
        if not current:
            current = [w]
            current_start_idx = i
            continue

        prev = current[-1]
        gap = w.start - prev.end
        token = prev.word

        # Decide if we should break after prev
        should_break = False

        # Hard break: sentence end or big gap
        if _ends_with(token, _HARD_PUNCT):
            should_break = True
        elif gap >= GAP_THRESHOLD:
            should_break = True
        # Soft break: comma/semicolon + enough words in chunk
        elif (
            _ends_with(token, _SOFT_PUNCT) and len(current) >= MIN_WORDS_FOR_COMMA_BREAK
        ):
            should_break = True
        # Hard max safeguard
        elif len(current) >= HARD_MAX_WORDS:
            should_break = True

        if should_break:
            flush_chunk(
                current_start_idx, current_start_idx + len(current) - 1, current
            )
            current = [w]
            current_start_idx = i
        else:
            current.append(w)

    # Flush last chunk
    flush_chunk(current_start_idx, current_start_idx + len(current) - 1, current)
    return chunks
