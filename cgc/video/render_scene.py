from __future__ import annotations

from pathlib import Path

from PIL import Image

from cgc.domain.types import Scene
from cgc.video.progress import draw_progress_bar
from cgc.video.render_board import render_board_image

FRAME_WIDTH = 1080
FRAME_HEIGHT = 1920
BOARD_SIZE = 1080  # keep board square at full width

_STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def render_scene_frame(
    scene: Scene,
    game_id: str,
    frames_dir: str,
    *,
    total_duration: float | None = None,
    flip_board: bool = False,
) -> str:
    """
    Render a single 1080×1920 portrait frame for a scene.

    - board scenes: render board from scene.raw["fen"] with last_move_uci.
    - text/intro scenes: render starting position, no highlight.
    - Subtitle text is handled by ASS; we just provide a clean top/bottom layout.
    """
    out_dir = Path(frames_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    frame = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT), color=(0, 0, 0))

    raw = scene.raw or {}

    if scene.type == "board":
        fen = raw.get("fen")
        last_move_uci = raw.get("last_move_uci")
    else:
        fen = _STARTING_FEN
        last_move_uci = None

    if fen:
        board_path = render_board_image(
            fen=fen,
            last_move_uci=last_move_uci,
            size=BOARD_SIZE,
            out_path=str(out_dir / f"{game_id}_{scene.index:02d}_{scene.id}_board.png"),
            flipped=flip_board,
        )
        board_img = Image.open(board_path).convert("RGB")

        # Ensure board fills width and is square
        board_img = board_img.resize((FRAME_WIDTH, FRAME_WIDTH))

        # Place board at the very top; subtitles occupy the lower area
        board_x = 0
        board_y = 0
        frame.paste(board_img, (board_x, board_y))

    # --- progress bar (optional) ---
    if total_duration is not None:
        draw_progress_bar(
            frame,
            current_time=scene.audio.start or 0.0,
            total_duration=total_duration,
        )

    out_path = out_dir / f"{game_id}_{scene.index:02d}_{scene.id}.png"
    frame.save(out_path, format="PNG")

    return str(out_path)
