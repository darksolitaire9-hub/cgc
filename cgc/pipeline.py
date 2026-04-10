# cgc/pipeline.py
from __future__ import annotations

import argparse
from pathlib import Path

from cgc.adapters.alignment import (
    build_alignment_manifest,
    build_fake_alignment_manifest,
)
from cgc.adapters.fetcher import extract_game_id, fetch_game
from cgc.adapters.storage import save_story
from cgc.adapters.subtitles import write_ass
from cgc.adapters.tts import build_audio_manifest, build_fake_audio_manifest
from cgc.config import PipelineConfig
from cgc.domain.alignment import apply_alignment_manifest
from cgc.domain.audio import apply_audio_manifest
from cgc.domain.story import (
    build_story,
    enrich_cards_with_positions,
    extract_meta,
    load_script,
    validate_script,
)
from cgc.domain.subtitles import build_subtitle_events
from cgc.domain.timeline import (
    assign_scene_timing,
    compute_total_duration,
)
from cgc.domain.types import Story
from cgc.domain.validation import (
    validate_scene_durations,
    validate_scene_order,
    validate_word_windows,
)
from cgc.video.assemble import assemble_video
from cgc.video.render_scene import render_scene_frame


def run_pipeline(
    script_path: str,
    device: str = "cpu",
    use_fake_tts: bool = True,
    use_fake_alignment: bool = True,
) -> Story:
    cfg = PipelineConfig()

    # 1) Load and validate storyboard
    script = load_script(script_path)
    validate_script(script)

    # 2) Fetch game
    game_url = script["source"]["value"]
    game_id = extract_game_id(game_url)
    game = fetch_game(game_id)

    # 3) Build story from YAML + PGN
    meta = extract_meta(game, script)
    enriched = enrich_cards_with_positions(game, script)
    story = build_story(enriched, game_id, meta)

    # 4) Audio manifest
    if use_fake_tts:
        audio_manifest = build_fake_audio_manifest(story, cfg, default_seconds=2.0)
    else:
        audio_manifest = build_audio_manifest(story, cfg)

    story = apply_audio_manifest(story, audio_manifest)

    # 5) Alignment manifest (fake or real)
    if use_fake_alignment:
        align_manifest = build_fake_alignment_manifest(story)
    else:
        align_manifest = build_alignment_manifest(
            story,
            audio_manifest,
            cfg,
            requested_device=device,
        )

    story = apply_alignment_manifest(story, align_manifest)

    # 6) Timeline: assign timing + validations + total duration
    story = assign_scene_timing(story)
    validate_scene_order(story)
    validate_scene_durations(story)

    # Only enforce word-level window constraints when alignment is real.
    if not use_fake_alignment:
        validate_word_windows(story)

    total = compute_total_duration(story)

    # 7) Subtitles (ASS)
    events = build_subtitle_events(story)
    ass_path = write_ass(game_id, events)

    # 8) Save canonical story JSON
    out_dir = Path("output/story")
    out_path = out_dir / f"{game_id}.json"
    story_json_path = save_story(story, str(out_path))

    print(
        f"game_id={story.game_id} scenes={len(story.scenes)} "
        f"total={total:.2f}s story={story_json_path} subs={ass_path}"
    )

    # 9) Render frames
    frames_dir = "output/frames"
    for scene in story.scenes:
        render_scene_frame(
            scene,
            game_id=story.game_id,
            frames_dir="output/frames",
            total_duration=total,
        )

    # 10) Assemble video
    # audio_path is None until real TTS is wired (step C in roadmap)
    merged_audio_path = audio_manifest.merged_audio_path  # None when fake
    video_path = assemble_video(
        story,
        frames_dir=frames_dir,
        audio_path=merged_audio_path,
        ass_path=ass_path,
        out_dir="output/video",
        fps=30,
    )
    print(f"video={video_path}")

    return story


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CGC pipeline")
    parser.add_argument("script", help="Path to storyboard YAML")
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default="cpu",
    )
    parser.add_argument(
        "--no-fake-tts",
        action="store_true",
        help="Use real TTS (not yet implemented)",
    )
    parser.add_argument(
        "--no-fake-alignment",
        action="store_true",
        help="Use real alignment (not yet implemented)",
    )

    args = parser.parse_args()

    if not Path(args.script).exists():
        print("script not found:", args.script)
        return

    run_pipeline(
        script_path=args.script,
        device=args.device,
        use_fake_tts=not args.no_fake_tts,
        use_fake_alignment=not args.no_fake_alignment,
    )


if __name__ == "__main__":
    main()
