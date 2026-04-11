from __future__ import annotations

from pathlib import Path
from typing import Any

import chess
from PIL import Image, ImageDraw, ImageFont

from cgc.config import (
    COLOR_ACCENT_GOLD,
    COLOR_BG_NARRATION,
    COLOR_BG_PLAYER_BAR,
    COLOR_EVAL_BG,
    COLOR_EVAL_LOSING,
    COLOR_EVAL_NEUTRAL,
    COLOR_EVAL_WINNING,
    COLOR_TEXT_DIM,
    COLOR_TEXT_PRIMARY,
    EVAL_STRIP_W,
    FONT_MONTSERRAT_BLACK,
    FONT_MONTSERRAT_BOLD,
    FONT_MONTSERRAT_MEDIUM,
    FONT_SIZE_BADGE,
    FONT_SIZE_CTA,
    FONT_SIZE_HOOK,
    FONT_SIZE_PLAYER,
    FONT_SIZE_RATING,
    SIDE_MARGIN,
    ZONE_BOARD_SIZE,
    ZONE_BOARD_Y,
    ZONE_NARRATION_H,
    ZONE_NARRATION_Y,
    ZONE_PLAYER_BAR_H,
    ZONE_PLAYER_BAR_Y,
)
from cgc.video.render_board import render_board_image

FRAME_W = 1080
FRAME_H = 1920


def _load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


FONT_HOOK = _load_font(FONT_MONTSERRAT_BLACK, FONT_SIZE_HOOK)
FONT_SUBTITLE = _load_font(
    FONT_MONTSERRAT_BOLD, FONT_SIZE_CTA
)  # unused here, kept for future
FONT_PLAYER_NAME = _load_font(FONT_MONTSERRAT_BOLD, FONT_SIZE_PLAYER)
FONT_RATING = _load_font(FONT_MONTSERRAT_MEDIUM, FONT_SIZE_RATING)
FONT_BADGE = _load_font(FONT_MONTSERRAT_MEDIUM, FONT_SIZE_BADGE)
FONT_CTA = _load_font(FONT_MONTSERRAT_BOLD, FONT_SIZE_CTA)


def _draw_player_bar(draw: ImageDraw.ImageDraw, meta: dict[str, Any]) -> None:
    # Background strip
    draw.rectangle(
        [(0, ZONE_PLAYER_BAR_Y), (FRAME_W, ZONE_PLAYER_BAR_Y + ZONE_PLAYER_BAR_H)],
        fill=COLOR_BG_PLAYER_BAR,
    )

    white = meta.get("white", "?")
    black = meta.get("black", "?")
    white_elo = meta.get("white_elo", "?")
    black_elo = meta.get("black_elo", "?")
    hero_color = meta.get("hero_color", meta.get("hero_color", "white"))

    if hero_color == "black":
        hero_name, hero_elo = black, black_elo
        opp_name, opp_elo = white, white_elo
    else:
        hero_name, hero_elo = white, white_elo
        opp_name, opp_elo = black, black_elo

    # Hero on the left
    y_center = ZONE_PLAYER_BAR_Y + ZONE_PLAYER_BAR_H // 2
    hero_x = SIDE_MARGIN
    opp_x = FRAME_W - SIDE_MARGIN

    # Hero name (gold)
    draw.text(
        (hero_x, y_center - 24),
        str(hero_name),
        font=FONT_PLAYER_NAME,
        fill=COLOR_ACCENT_GOLD,
    )
    # Hero rating (dim)
    draw.text(
        (hero_x, y_center + 12),
        str(hero_elo),
        font=FONT_RATING,
        fill=COLOR_TEXT_DIM,
    )

    # Opponent name (primary)
    opp_name_text = str(opp_name)
    name_bbox = FONT_PLAYER_NAME.getbbox(opp_name_text)
    opp_name_w = name_bbox[2] - name_bbox[0]
    draw.text(
        (opp_x - opp_name_w, y_center - 24),
        opp_name_text,
        font=FONT_PLAYER_NAME,
        fill=COLOR_TEXT_PRIMARY,
    )
    # Opponent rating (dim)
    opp_elo_text = str(opp_elo)
    elo_bbox = FONT_RATING.getbbox(opp_elo_text)
    opp_elo_w = elo_bbox[2] - elo_bbox[0]
    draw.text(
        (opp_x - opp_elo_w, y_center + 12),
        opp_elo_text,
        font=FONT_RATING,
        fill=COLOR_TEXT_DIM,
    )


def _draw_move_badge(draw: ImageDraw.ImageDraw, ply: int | None) -> None:
    if ply is None:
        return
    text = f"Move {ply}"
    bbox = FONT_BADGE.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = FRAME_W - SIDE_MARGIN - text_w
    y = ZONE_BOARD_Y + ZONE_BOARD_SIZE - text_h - 16
    draw.text(
        (x, y),
        text,
        font=FONT_BADGE,
        fill=COLOR_ACCENT_GOLD,
    )


def _draw_outro_text(frame: Image.Image, lines: list[str]) -> None:
    if not lines:
        return
    draw = ImageDraw.Draw(frame)
    zone_top = ZONE_NARRATION_Y
    zone_bottom = ZONE_NARRATION_Y + ZONE_NARRATION_H
    y = zone_top + 20
    for line in lines:
        if not line:
            continue

        text = str(line)
        bbox = FONT_CTA.getbbox(text)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (FRAME_W - text_w) // 2
        draw.text(
            (x, y),
            text,
            font=FONT_CTA,
            fill=COLOR_ACCENT_GOLD,
        )
        y += text_h + 8
        if y > zone_bottom:
            break


def render_scene_frame(
    scene,
    game_id: str,
    frames_dir: str,
    *,
    flip_board: bool,
    ending_fen: str | None,
    meta: dict[str, Any],
    total_duration: float,
) -> None:
    """
    Compose a single frame for the given scene using the Layout v2 4‑zone design.
    """
    # Base canvas
    frame = Image.new("RGB", (FRAME_W, FRAME_H), (0, 0, 0))
    draw = ImageDraw.Draw(frame)

    # Player bar — full data from Story.meta
    _draw_player_bar(draw, meta)

    # Narration zone background
    draw.rectangle(
        [(0, ZONE_NARRATION_Y), (FRAME_W, ZONE_NARRATION_Y + ZONE_NARRATION_H)],
        fill=COLOR_BG_NARRATION,
    )

    # Determine which FEN to show
    fen = None
    if scene.type == "board":
        fen = (scene.raw or {}).get("fen")
    elif scene.type == "text":
        # intro-* shows starting FEN, outro-* shows ending_fen
        sid = scene.id or ""
        if sid.startswith("intro"):
            fen = chess.STARTING_FEN
        elif sid.startswith("outro") and ending_fen is not None:
            fen = ending_fen

    if fen is None:
        # Fallback: starting position
        fen = chess.STARTING_FEN

    # Render board image via SVG->PNG pipeline, then load and resize
    board_path = render_board_image(
        fen=fen,
        last_move_uci=(scene.raw or {}).get("last_move_uci"),
        size=ZONE_BOARD_SIZE,
        flipped=flip_board,
    )
    board_img = Image.open(board_path).convert("RGB")
    board_img = board_img.resize((ZONE_BOARD_SIZE, ZONE_BOARD_SIZE), Image.LANCZOS)
    frame.paste(board_img, (0, ZONE_BOARD_Y))

    # Move badge
    _draw_move_badge(draw, getattr(scene, "ply", None))

   

    # Save frame
    out_dir = Path(frames_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{game_id}_{scene.index:02d}_{scene.id}.png"
    frame.save(out_path)
