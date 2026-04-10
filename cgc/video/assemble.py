from __future__ import annotations

import platform
import subprocess
from pathlib import Path

import imageio.v3 as iio
import numpy as np

from cgc.domain.timeline import compute_total_duration
from cgc.domain.types import Story


# ---------------------------------------------------------------------------
# Path utilities
# ---------------------------------------------------------------------------

def _resolve_path(p: str | Path) -> str:
    """
    Return a path string safe for use anywhere in this module.

    - On Windows: backslashes → forward slashes, drive colon escaped to \\:
      (required by ffmpeg -vf ass= and -i on Windows)
    - On POSIX: returns the POSIX string unchanged.

    Accepts both str and Path objects.
    """
    posix = Path(p).as_posix()  # always forward slashes, works on all OS
    if platform.system() == "Windows" and len(posix) > 1 and posix[1] == ":":
        posix = posix[0] + "\\:" + posix[2:]
    return posix


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

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
        macro_block_size=2,  # keeps 1080×1920 exact — no silent resize
    )


def _mux_audio(video_path: Path, audio_path: Path, out_path: Path) -> None:
    """Mux external WAV/AAC into the video, trimmed to video length."""
    cmd = [
        "ffmpeg", "-y",
        "-i", _resolve_path(video_path),
        "-i", _resolve_path(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        _resolve_path(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio mux failed:\n{result.stderr}")


def _burn_subtitles(
    video_path: Path,
    ass_path: Path,
    out_path: Path,
    total_duration: float,
) -> None:
    """
    Hard-burn ASS subtitles via -vf ass=, then fade video to black at the end.
    Preferred over soft subs for vertical/social MP4 compatibility.
    _resolve_path handles Windows drive-letter escaping automatically.
    """
    fade_duration = 0.5  # seconds, video-only fade
    fade_start = max(0.0, total_duration - fade_duration)

    vf_filter = (
        f"ass={_resolve_path(ass_path)},"
        f"fade=t=out:st={fade_start}:d={fade_duration}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", _resolve_path(video_path),
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-c:a", "copy",
        _resolve_path(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg subtitle burn failed:\n{result.stderr}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

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
      3. If ass_path given: burn ASS subtitles and fade video to black.

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

    # --- Step 3: subtitle burn + video fade ---
    if ass_path:
        final_path = out_root / f"{game_id}.mp4"
        print(f"[assemble] step 3/3 — burning subtitles + fade → {final_path}")
        _burn_subtitles(current_path, Path(ass_path), final_path, total_duration=total)
        current_path = final_path
    else:
        print("[assemble] step 3/3 — skipped (no ass_path)")

    print(f"[assemble] done → {current_path}")
    return str(current_path)