# cgc/video/render_scene.py
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from cgc.domain.types import Scene
from cgc.video.render_board import render_board_image

FRAME_WIDTH = 1080
FRAME_HEIGHT = 1920
BOARD_SIZE = 1080

# Standard starting position FEN — used for intro (text-type) scenes
# that have no fen in raw.
_STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def render_scene_frame(
    scene: Scene,
    game_id: str,
    frames_dir: str = "output/frames",
) -> str:
    """
    Render a single 1080x1920 portrait frame for a scene.

    Rules:
    - Board scenes (type == "board"): render board from scene.raw["fen"].
    - Text/intro scenes (type == "text"): render the starting position board
      with no move highlight (pieces only, no last-move square).
    - NO display_lines text is drawn — all text is carried by ASS subtitles.

    The bottom 840px (below the board) is left black — subtitles burn in there.
    """
    out_dir = Path(frames_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    frame = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT), color=(0, 0, 0))

    raw = scene.raw or {}

    if scene.type == "board":
        fen = raw.get("fen")
        last_move_uci = raw.get("last_move_uci")
    else:
        # text / intro / outro — show starting position, no highlight
        fen = _STARTING_FEN
        last_move_uci = None

    if fen:
        board_path = render_board_image(
            fen=fen,
            last_move_uci=last_move_uci,
            size=BOARD_SIZE,
            out_path=str(out_dir / f"{game_id}_{scene.index:02d}_{scene.id}_board.png"),
        )
        board_img = Image.open(board_path).convert("RGB")
        board_img = board_img.resize((BOARD_SIZE, BOARD_SIZE))
        frame.paste(board_img, (0, 0))

    out_path = out_dir / f"{game_id}_{scene.index:02d}_{scene.id}.png"
    frame.save(out_path, format="PNG")
    return str(out_path)
