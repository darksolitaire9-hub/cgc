from __future__ import annotations

import platform
import subprocess
from pathlib import Path

from cgc.domain.timeline import compute_total_duration
from cgc.domain.types import Story
from cgc.video.progress import build_progress_filter_parts

# ---------------------------------------------------------------------------
# Path utilities
# ---------------------------------------------------------------------------


def _resolve_path(p: str | Path) -> str:
    """Return a path string safe for ffmpeg command-line arguments."""
    posix = Path(p).as_posix()
    if platform.system() == "Windows" and len(posix) > 1 and posix[1] == ":":
        posix = posix[0] + "\\\\:" + posix[2:]
    return posix


def _run_ffmpeg(cmd: list[str]) -> None:
    """Run an ffmpeg command, raising RuntimeError with stderr on failure."""
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed:\n{e.stderr}") from e


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _scene_png_path(frames_dir: Path, game_id: str, scene) -> Path:
    return frames_dir / f"{game_id}_{scene.index:02d}_{scene.id}.png"


def _write_concat_file(story: Story, frames_dir: Path, concat_path: Path) -> None:
    """Write an ffmpeg concat demuxer input file."""
    lines: list[str] = []
    last_posix: str | None = None

    for scene in story.scenes:
        if scene.audio.start is None or scene.audio.end is None:
            raise ValueError(f"Scene {scene.id!r} has no timing.")

        duration = scene.audio.end - scene.audio.start
        png_path = _scene_png_path(frames_dir, story.game_id, scene)

        if not png_path.exists():
            raise FileNotFoundError(f"Frame not found: {png_path}")

        posix = png_path.resolve().as_posix()
        lines.append(f"file '{posix}'")
        lines.append(f"duration {duration:.6f}")
        last_posix = posix

    if last_posix is not None:
        lines.append(f"file '{last_posix}'")

    concat_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Processing Passes
# ---------------------------------------------------------------------------


def _encode_video_only(
    story: Story, frames_dir: Path, out_path: Path, fps: int
) -> None:
    """Step 1: Raw assembly of frames."""
    concat_path = out_path.parent / f"{story.game_id}_concat.txt"
    try:
        _write_concat_file(story, frames_dir, concat_path)
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            _resolve_path(concat_path),
            "-vf",
            f"fps={fps},format=yuv420p",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "ultrafast",
            _resolve_path(out_path),
        ]
        _run_ffmpeg(cmd)  # ← was subprocess.run(...)
    finally:
        concat_path.unlink(missing_ok=True)


def _mux_audio(video_path: Path, audio_path: Path, out_path: Path) -> None:
    """Step 2: Add audio stream."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        _resolve_path(video_path),
        "-i",
        _resolve_path(audio_path),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        _resolve_path(out_path),
    ]
    _run_ffmpeg(cmd)  # ← was subprocess.run(...)


def _burn_final_overlays(
    video_path: Path,
    ass_path: Path | None,
    out_path: Path,
    total_duration: float,
    fps: int,
) -> None:
    fade_dur = 0.5
    fade_start = max(0.0, total_duration - fade_dur)

    track_f, fill_src, overlay_f = build_progress_filter_parts(total_duration, fps)

    fc: list[str] = [
        f"[0:v]{track_f}[track]",
        f"{fill_src}[fill]",
        f"[track][fill]{overlay_f}[bar]",
    ]
    current = "[bar]"

    if ass_path and ass_path.exists():
        fc.append(f"{current}ass='{_resolve_path(ass_path)}'[subs]")
        current = "[subs]"

    fc.append(f"{current}fade=t=out:st={fade_start:.3f}:d={fade_dur}[out]")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        _resolve_path(video_path),
        "-filter_complex",
        ";".join(fc),
        "-map",
        "[out]",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "fast",
        "-c:a",
        "copy",
        _resolve_path(out_path),
    ]
    _run_ffmpeg(cmd)  # ← was subprocess.run(...)


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
    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    total = compute_total_duration(story)

    v_tmp = out_root / f"{story.game_id}_v.mp4"
    _encode_video_only(story, Path(frames_dir), v_tmp, fps)

    current = v_tmp
    if audio_path:
        a_tmp = out_root / f"{story.game_id}_va.mp4"
        _mux_audio(current, Path(audio_path), a_tmp)
        current = a_tmp

    final = out_root / f"{story.game_id}.mp4"
    try:
        _burn_final_overlays(
            current,
            Path(ass_path) if ass_path else None,
            final,
            total,
            fps,
        )
    finally:
        for tmp in [v_tmp, out_root / f"{story.game_id}_va.mp4"]:
            if tmp.exists() and tmp != final:
                tmp.unlink()

    return str(final)
