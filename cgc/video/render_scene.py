from __future__ import annotations

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont  # Pillow [web:106][web:108]

from cgc.domain.types import Scene
from cgc.video.render_board import render_board_image

FRAME_WIDTH = 1080
FRAME_HEIGHT = 1920
BOARD_SIZE = 1080  # square board at top


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    # Try a common font; fall back to default.
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _wrap_lines(
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    draw: ImageDraw.ImageDraw,
) -> str:
    # Simple word-wrap using textlength, based on common Pillow patterns. [web:110][web:113]
    words = text.split()
    lines: list[str] = []
    buf: list[str] = []

    for word in words:
        test_line = " ".join(buf + [word])
        width = draw.textlength(test_line, font=font)
        if width <= max_width:
            buf.append(word)
        else:
            if buf:
                lines.append(" ".join(buf))
            buf = [word]

    if buf:
        lines.append(" ".join(buf))

    return "\n".join(lines)


def _scene_text(scene: Scene) -> str:
    # Use display_lines joined; spoken_text may be too long for overlay.
    return " ".join(scene.display_lines)


def render_scene_frame(
    scene: Scene,
    game_id: str,
    frames_dir: str = "output/frames",
) -> str:
    """
    Render a single portrait scene frame (1080x1920) with:

    - Board at top (square, full width) for board scenes.
    - Text area in the bottom region.
    """
    out_dir = Path(frames_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    frame = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(frame)

    # 1) Board region
    if scene.type == "board":
        # If you stored fen/last_move_uci in scene.raw, use that.
        raw = scene.raw or {}
        fen = raw.get("fen")
        last_move_uci = raw.get("last_move_uci")

        if fen:
            board_path = render_board_image(
                fen=fen,
                last_move_uci=last_move_uci,
                size=BOARD_SIZE,
                out_path=str(
                    out_dir / f"{game_id}_{scene.index:02d}_{scene.id}_board.png"
                ),
            )
            board_img = Image.open(board_path).convert("RGB")
            board_img = board_img.resize((BOARD_SIZE, BOARD_SIZE))

            # Top-aligned, full width: paste at (0, 0).
            frame.paste(board_img, (0, 0))

    # 2) Text region (bottom)
    text = _scene_text(scene)
    if text:
        font = _load_font(40)
        margin = 40
        text_top = BOARD_SIZE + margin  # start below board
        max_width = FRAME_WIDTH - 2 * margin

        wrapped = _wrap_lines(text, font, max_width, draw)

        # Draw a slight translucent background behind text (optional)
        # For now, simple white text on black bg is fine.
        draw.multiline_text(
            (margin, text_top),
            wrapped,
            font=font,
            fill=(255, 255, 255),
            spacing=8,
        )

    out_path = out_dir / f"{game_id}_{scene.index:02d}_{scene.id}.png"
    frame.save(out_path, format="PNG")

    return str(out_path)
