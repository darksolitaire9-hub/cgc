from __future__ import annotations

from io import StringIO
from urllib.parse import urlparse

import chess.pgn
import requests

LICHESS_GAME_API = "https://lichess.org/game/export/{game_id}"


def extract_game_id(url: str) -> str:
    """
    Extract the Lichess game id from a standard game URL, e.g.:

      https://lichess.org/1ORTExZg
      https://lichess.org/1ORTExZg/black
      https://lichess.org/1ORTExZg#32

    Returns the bare game id (e.g. '1ORTExZg').

    Raises ValueError if it cannot parse a plausible id.
    """
    parsed = urlparse(url)
    path = parsed.path.strip("/")  # e.g. "1ORTExZg" or "1ORTExZg/black"
    if not path:
        raise ValueError(f"cannot extract game id from url={url!r}")

    parts = path.split("/")
    game_id = parts[0]
    if not game_id:
        raise ValueError(f"cannot extract game id from url={url!r}")

    return game_id


def fetch_game(game_id: str) -> chess.pgn.Game:
    """
    Fetch a single Lichess game as PGN and parse it into a python-chess Game.

    Uses the public export endpoint with ?clocks=false ?evals=false etc. for simplicity.
    """
    url = LICHESS_GAME_API.format(game_id=game_id)
    # Simplest form: a single PGN text response. [web:52][web:53]
    resp = requests.get(
        url,
        params={
            "moves": "true",
            "pgnInJson": "false",
            "clocks": "false",
            "evals": "false",
        },
        timeout=10,
    )
    resp.raise_for_status()
    pgn_text = resp.text

    handle = StringIO(pgn_text)
    game = chess.pgn.read_game(handle)  # python-chess PGN reader [web:20][web:47]
    if game is None:
        raise ValueError(f"no game found in PGN for id={game_id!r}")

    return game
