from __future__ import annotations

from pathlib import Path
from typing import Optional

import chess
import chess.svg
from cairosvg import svg2png  # small, focused SVG->PNG tool [web:99]


def render_board_image(
    fen: str,
    last_move_uci: Optional[str] = None,
    size: int = 720,
    out_path: str | None = None,
) -> str:
    """
    Render a chess board image from FEN (and optional last move) to a PNG file.

    - Uses python-chess' chess.svg.board() for board+pieces. [web:87][web:92]
    - Converts SVG to PNG via cairosvg.svg2png(). [web:99]
    """
    board = chess.Board(fen)

    lastmove = None
    if last_move_uci:
        try:
            lastmove = chess.Move.from_uci(last_move_uci)
        except ValueError:
            lastmove = None

    svg_text = chess.svg.board(
        board=board,
        lastmove=lastmove,
        size=size,
    )  # returns SVG string [web:87][web:97]

    if out_path is None:
        out_path = "output/frames/board.png"

    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    svg2png(bytestring=svg_text.encode("utf-8"), write_to=str(path))  # [web:99]

    return str(path)