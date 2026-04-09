from __future__ import annotations

from pathlib import Path

import imageio.v3 as iio

from cgc.domain.types import Story
from cgc.domain.timeline import compute_total_duration
from cgc.video.render_scene import render_placeholder_frame


def assemble_video(
    story: Story,
    *,
    fps: int = 30,
    out_dir: str = "output/video",
) -> str:
    """
    Minimal assembler: render one placeholder frame per scene and
    write a constant-length video based on the timeline.
    No audio or subtitles muxing yet.
    """
    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    out_path = out_root / f"{story.game_id}.mp4"

    # For now, we just repeat frames so length ≈ total duration.
    total = compute_total_duration(story)
    total_frames = max(1, int(total * fps))

    # Render one frame per scene (re-use last for extra frames).
    per_scene_frames = max(1, total_frames // max(1, len(story.scenes)))
    frames = []
    for scene in story.scenes:
        frame = render_placeholder_frame(scene)
        frames.extend([frame] * per_scene_frames)

    # Adjust to exact frame count
    frames = frames[:total_frames]

    iio.imwrite(
        out_path,
        frames,
        fps=fps,
        codec="libx264",
        pixelformat="yuv420p",
    )

    return str(out_path)