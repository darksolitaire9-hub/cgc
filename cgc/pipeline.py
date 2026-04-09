from __future__ import annotations

from pathlib import Path

from cgc.adapters.fetcher import extract_game_id, fetch_game
from cgc.domain.story import (
    build_story,
    enrich_cards_with_positions,
    extract_meta,
    load_script,
    validate_script,
)
from cgc.domain.timeline import (
    assign_scene_timing,
    compute_total_duration,
    with_default_durations,
)


def build_story_from_script(script_path: str) -> None:
    script = load_script(script_path)
    validate_script(script)

    game_url = script["source"]["value"]
    game_id = extract_game_id(game_url)
    game = fetch_game(game_id)
    meta = extract_meta(game)

    enriched = enrich_cards_with_positions(game, script)
    story = build_story(enriched, game_id, meta)

    story = with_default_durations(story, default_seconds=2.0)
    story = assign_scene_timing(story)
    total = compute_total_duration(story)

    print(f"game_id={story.game_id} scenes={len(story.scenes)} total={total:.2f}s")


if __name__ == "__main__":
    script_path = "scripts/example.yaml"
    if Path(script_path).exists():
        build_story_from_script(script_path)
    else:
        print("script not found:", script_path)
