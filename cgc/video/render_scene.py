from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from cgc.domain.types import Scene


def render_placeholder_frame(scene: Scene, *, size: tuple[int, int] = (1080, 1920)) -> Image.Image:
    """
    Minimal renderer: solid background + scene id text.
    This is only for pipeline testing before real board rendering.
    """
    w, h = size
    img = Image.new("RGBA", (w, h), "#141414")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("fonts/Inter-Bold.otf", 72)
    except OSError:
        font = ImageFont.load_default()

    text = f"{scene.index:02d} - {scene.id}"
    draw.text((w // 2, h // 2), text, fill="#FFFFFF", font=font, anchor="mm")

    return img