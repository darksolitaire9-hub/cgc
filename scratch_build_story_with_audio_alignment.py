from cgc.adapters.alignment import build_fake_alignment_manifest
from cgc.adapters.fetcher import extract_game_id, fetch_game
from cgc.adapters.storage import save_story
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


def main(script_path: str) -> None:
    script = load_script(script_path)
    validate_script(script)

    game_url = script["source"]["value"]
    game_id = extract_game_id(game_url)
    game = fetch_game(game_id)

    meta = extract_meta(game, script)
    enriched = enrich_cards_with_positions(game, script)
    story = build_story(enriched, game_id, meta)

    audio_manifest = build_fake_audio_manifest(story, default_seconds=2.0)
    story_with_audio = apply_audio_manifest(story, audio_manifest)

    align_manifest = build_fake_alignment_manifest(story_with_audio)
    story_full = apply_alignment_manifest(story_with_audio, align_manifest)

    out_path = f"output/story/{game_id}_with_audio_alignment.json"
    path = save_story(story_full, out_path)
    print("wrote story with audio+alignment:", path)


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
