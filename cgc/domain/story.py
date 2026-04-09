from __future__ import annotations

from pathlib import Path
from typing import Any

import chess.pgn
import yaml

from cgc.domain.types import Scene, Story, VisualInfo


def load_script(script_path: str) -> dict:
    path = Path(script_path)
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text)


def validate_script(script: dict) -> None:
    if "source" not in script or "cards" not in script:
        raise ValueError("Script must contain 'source' and 'cards'")
    if "value" not in script["source"]:
        raise ValueError("script['source'] must contain 'value'")


def extract_meta(game: chess.pgn.Game) -> dict[str, Any]:
    h = game.headers
    return {
        "white": h.get("White", "?"),
        "black": h.get("Black", "?"),
        "white_elo": h.get("WhiteElo", "?"),
        "black_elo": h.get("BlackElo", "?"),
        "result": h.get("Result", "?"),
        "opening": h.get("Opening", ""),
    }


def enrich_cards_with_positions(game: chess.pgn.Game, script: dict) -> dict:
    """Return a new script dict with fen / last_move_uci added where ply is set."""
    board = game.board()
    moves = list(game.mainline_moves())

    ply_to_fen: dict[int, str] = {0: chess.STARTING_FEN}
    ply_to_last_uci: dict[int, str] = {}

    for i, move in enumerate(moves, start=1):
        board.push(move)
        ply_to_fen[i] = board.fen()
        ply_to_last_uci[i] = move.uci()

    # shallow copy; cards list reused but entries mutated – fine for now
    script = dict(script)
    cards = list(script.get("cards") or [])
    for card in cards:
        ply = card.get("ply")
        if not isinstance(ply, int):
            continue
        if ply in ply_to_fen:
            card["fen"] = ply_to_fen[ply]
        if ply in ply_to_last_uci:
            card["last_move_uci"] = ply_to_last_uci[ply]

    script["cards"] = cards
    return script


def _spoken_text_from_card(card: dict) -> str:
    if card.get("voiceover"):
        return str(card["voiceover"]).strip()
    lines = [str(line).strip() for line in card.get("lines", []) if str(line).strip()]
    return " ".join(lines)


def build_story(script: dict, game_id: str, meta: dict) -> Story:
    scenes: list[Scene] = []

    for i, card in enumerate(script["cards"]):
        scene = Scene(
            index=i,
            id=card["id"],
            type=card["type"],
            role=card.get("role"),
            ply=card.get("ply"),
            display_lines=card.get("lines", []),
            spoken_text=_spoken_text_from_card(card),
            visual=VisualInfo(highlight_mode=(card.get("highlight") or {}).get("mode")),
            raw=card,
        )
        scenes.append(scene)

    return Story(
        game_id=game_id,
        source_url=script["source"]["value"],
        meta=meta,
        scenes=scenes,
    )
