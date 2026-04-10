from __future__ import annotations

from pathlib import Path
from typing import Any

import chess
import chess.pgn
import yaml

from cgc.adapters.fetcher import resolve_hero_color
from cgc.domain.types import Scene, Story, VisualInfo
from cgc.settings.user import HERO_USERNAME

META_KEY_VOICE = "voice"
META_KEY_PERSPECTIVE = "perspective"
META_KEY_HERO_USERNAME = "hero_username"
META_KEY_HERO_COLOR = "hero_color"


def load_script(script_path: str) -> dict:
    path = Path(script_path)
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("script root must be a mapping")
    return data


def validate_script(script: dict) -> None:
    if "source" not in script or "cards" not in script:
        raise ValueError("script must contain 'source' and 'cards'")

    src = script["source"]
    if not isinstance(src, dict):
        raise ValueError("script['source'] must be a mapping")

    if "type" not in src or "value" not in src:
        raise ValueError("script['source'] must contain 'type' and 'value'")

    if src["type"] != "lichess_url":
        raise ValueError(f"unsupported source.type={src['type']!r}")

    if not isinstance(script["cards"], list):
        raise ValueError("script['cards'] must be a list")


def extract_meta(game: chess.pgn.Game, script: dict) -> dict[str, Any]:
    headers = game.headers
    hero_from_script = (script.get("source") or {}).get("hero")

    white_name = headers.get("White", "?")
    black_name = headers.get("Black", "?")
    white_elo = headers.get("WhiteElo", "?")
    black_elo = headers.get("BlackElo", "?")

    hero_color = resolve_hero_color(
        white_name=white_name,
        black_name=black_name,
        white_elo=white_elo,
        black_elo=black_elo,
        hero_username=HERO_USERNAME,
    )

    return {
        "white": white_name,
        "black": black_name,
        "white_elo": white_elo,
        "black_elo": black_elo,
        "result": headers.get("Result", "?"),
        "opening": headers.get("Opening", ""),
        "hero": hero_from_script,
        META_KEY_HERO_USERNAME: HERO_USERNAME,
        META_KEY_HERO_COLOR: hero_color,
    }


def enrich_cards_with_positions(
    game: chess.pgn.Game,
    script: dict,
) -> dict:
    board = game.board()
    moves = list(game.mainline_moves())

    ply_to_fen: dict[int, str] = {0: chess.STARTING_FEN}
    ply_to_last_uci: dict[int, str] = {}

    for i, move in enumerate(moves, start=1):
        board.push(move)
        ply_to_fen[i] = board.fen()
        ply_to_last_uci[i] = move.uci()

    script_copy = dict(script)
    cards = list(script_copy.get("cards") or [])

    for card in cards:
        if not isinstance(card, dict):
            continue
        ply = card.get("ply")
        if not isinstance(ply, int):
            continue

        fen = ply_to_fen.get(ply)
        if fen is not None:
            card["fen"] = fen

        last_uci = ply_to_last_uci.get(ply)
        if last_uci is not None:
            card["last_move_uci"] = last_uci

    script_copy["cards"] = cards
    return script_copy


def _spoken_text_from_card(card: dict) -> str:
    voiceover = card.get("voiceover")
    if voiceover is not None:
        text = str(voiceover).strip()
        if text:
            return text

    lines = [str(line).strip() for line in card.get("lines", []) if str(line).strip()]
    return " ".join(lines)


def build_story(script: dict, game_id: str, meta: dict[str, Any]) -> Story:
    scenes: list[Scene] = []

    cards = script.get("cards") or []
    for i, card in enumerate(cards):
        if not isinstance(card, dict):
            continue

        scene = Scene(
            index=i,
            id=card["id"],
            type=card["type"],
            role=card.get("role"),
            ply=card.get("ply"),
            display_lines=list(card.get("lines", [])),
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
