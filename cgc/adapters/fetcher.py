import io

import chess.pgn
import requests

LICHESS_EXPORT = "https://lichess.org/game/export/{game_id}"


def extract_game_id(lichess_url: str) -> str:
    return lichess_url.rstrip("/").split("/")[-1]


def fetch_game(game_id: str, *, timeout: float = 20.0) -> chess.pgn.Game:
    url = LICHESS_EXPORT.format(game_id=game_id)
    resp = requests.get(url, params={"clocks": "true", "evals": "true"}, timeout=timeout)
    resp.raise_for_status()
    return chess.pgn.read_game(io.StringIO(resp.text))