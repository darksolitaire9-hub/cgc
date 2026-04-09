# cgc/video/assemble.py
from __future__ import annotations

import subprocess
from pathlib import Path

import imageio.v3 as iio
import numpy as np

from cgc.domain.timeline import compute_total_duration
from cgc.domain.types import Story


def _scene_png_path(frames_dir: Path, game_id: str, scene) -> Path:
    """Reconstruct the exact path that render_scene_frame writes."""
    return frames_dir / f"{game_id}_{scene.index:02d}_{scene.id}.png"


def _encode_video_only(
    story: Story,
    frames_dir: Path,
    out_path: Path,
    fps: int,
) -> None:
    """
    Hold each scene's PNG for round(duration * fps) frames and write
    a silent libx264 MP4. Fails loudly on missing PNGs or bad timing.
    """
    frame_list: list[np.ndarray] = []

    for scene in story.scenes:
        if scene.audio.start is None or scene.audio.end is None:
            raise ValueError(
                f"Scene {scene.id!r} has no timing — run assign_scene_timing first."
            )
        duration = scene.audio.end - scene.audio.start
        if duration <= 0:
            raise ValueError(
                f"Scene {scene.id!r} has non-positive duration: {duration:.3f}s"
            )
        png_path = _scene_png_path(frames_dir, story.game_id, scene)
        if not png_path.exists():
            raise FileNotFoundError(
                f"Frame not found for scene {scene.id!r}: {png_path}\n"
                "Run render_scene_frame for all scenes before assembling."
            )
        frame = iio.imread(png_path)  # HWC uint8
        n_frames = max(1, round(duration * fps))
        frame_list.extend([frame] * n_frames)

    iio.imwrite(
        str(out_path),
        frame_list,
        fps=fps,
        codec="libx264",
        pixelformat="yuv420p",
    )


def _mux_audio(video_path: Path, audio_path: Path, out_path: Path) -> None:
    """Mux external WAV/AAC into the video, trimmed to video length."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio mux failed:\n{result.stderr}")


def _burn_subtitles(video_path: Path, ass_path: Path, out_path: Path) -> None:
    """
    Hard-burn ASS subtitles via -vf ass=.
    Preferred over soft subs for vertical/social MP4 compatibility.
    Uses forward slashes for the ass= filter path (required on Windows too).
    """
    ass_str = ass_path.as_posix()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vf",
        f"ass={ass_str}",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "fast",
        "-c:a",
        "copy",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg subtitle burn failed:\n{result.stderr}")


def assemble_video(
    story: Story,
    *,
    frames_dir: str = "output/frames",
    audio_path: str | None = None,
    ass_path: str | None = None,
    out_dir: str = "output/video",
    fps: int = 30,
) -> str:
    """
    Assemble final MP4 from pre-rendered scene PNGs.

    Steps (each is a discrete ffmpeg pass):
      1. Encode video-only MP4: each PNG held for its scene's audio duration.
      2. If audio_path given: mux audio (AAC 192k, trimmed to video length).
      3. If ass_path given: burn ASS subtitles (hard-coded, social-compatible).

    Args:
        story:      Fully-timed Story (assign_scene_timing must have run).
        frames_dir: Directory containing PNGs from render_scene_frame.
        audio_path: Path to merged WAV/AAC (None = video-only output).
        ass_path:   Path to .ass subtitle file (None = no subtitles).
        out_dir:    Output directory for all intermediate and final MP4s.
        fps:        Frames per second (default 30).

    Returns:
        Absolute path to the final output MP4.

    Raises:
        FileNotFoundError: A scene PNG is missing.
        ValueError:        A scene has missing or invalid timing.
        RuntimeError:      An ffmpeg pass failed (stderr included).
    """
    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    frames_path = Path(frames_dir)

    game_id = story.game_id
    total = compute_total_duration(story)
    print(
        f"[assemble] game={game_id} scenes={len(story.scenes)} "
        f"total={total:.2f}s fps={fps}"
    )

    # Intermediate names avoid clobbering the final output on re-runs.
    needs_intermediate = bool(audio_path or ass_path)
    video_only_path = (
        out_root / f"{game_id}_video_only.mp4"
        if needs_intermediate
        else out_root / f"{game_id}.mp4"
    )

    # --- Step 1: video-only ---
    print(f"[assemble] step 1/3 — encoding frames → {video_only_path}")
    _encode_video_only(story, frames_path, video_only_path, fps)
    current_path = video_only_path

    # --- Step 2: audio mux ---
    if audio_path:
        audio_muxed_path = out_root / f"{game_id}_with_audio.mp4"
        print(f"[assemble] step 2/3 — muxing audio → {audio_muxed_path}")
        _mux_audio(current_path, Path(audio_path), audio_muxed_path)
        current_path = audio_muxed_path
    else:
        print("[assemble] step 2/3 — skipped (no audio_path)")

    # --- Step 3: subtitle burn ---
    if ass_path:
        final_path = out_root / f"{game_id}.mp4"
        print(f"[assemble] step 3/3 — burning subtitles → {final_path}")
        _burn_subtitles(current_path, Path(ass_path), final_path)
        current_path = final_path
    else:
        print("[assemble] step 3/3 — skipped (no ass_path)")

    print(f"[assemble] done → {current_path}")
    return str(current_path)
