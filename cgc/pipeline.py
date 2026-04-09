from __future__ import annotations

import argparse
from pathlib import Path

from cgc.adapters.alignment import build_fake_alignment_manifest
from cgc.adapters.fetcher import extract_game_id, fetch_game
from cgc.adapters.storage import save_story
from cgc.adapters.subtitles import write_ass
from cgc.adapters.tts import build_fake_audio_manifest
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
    validate_scene_durations,
    validate_scene_order,
    validate_word_windows,
)
from cgc.domain.types import Story


def run_pipeline(
    script_path: str,
    device: str = "cpu",
    use_fake_tts: bool = True,
    use_fake_alignment: bool = True,
) -> Story:
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

    # 4) Audio manifest (fake for now)
    if use_fake_tts:
        audio_manifest = build_fake_audio_manifest(story, default_seconds=2.0)
    else:
        raise NotImplementedError("real TTS manifest not wired yet")

    story = apply_audio_manifest(story, audio_manifest)

    # 5) Alignment manifest (fake for now)
    if use_fake_alignment:
        align_manifest = build_fake_alignment_manifest(story)
    else:
        raise NotImplementedError("real alignment manifest not wired yet")

    story = apply_alignment_manifest(story, align_manifest)

    # 6) Timeline: assign timing + validations + total duration
    story = assign_scene_timing(story)
    validate_scene_order(story)
    validate_scene_durations(story)
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
    return story


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CGC pipeline")
    parser.add_argument("script", help="Path to storyboard YAML")
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default="cpu",
        help="Device for alignment/TTS (reserved for real adapters later)",
    )
    parser.add_argument(
        "--no-fake-tts",
        action="store_true",
        help="Disable fake TTS manifest (real TTS not yet implemented)",
    )
    parser.add_argument(
        "--no-fake-alignment",
        action="store_true",
        help="Disable fake alignment manifest (real alignment not yet implemented)",
    )

    args = parser.parse_args()

    script_path = args.script
    device = args.device

    if not Path(script_path).exists():
        print("script not found:", script_path)
        return

    run_pipeline(
        script_path=script_path,
        device=device,
        use_fake_tts=not args.no_fake_tts,
        use_fake_alignment=not args.no_fake_alignment,
    )


if __name__ == "__main__":
    main()
