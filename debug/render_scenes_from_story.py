import json
from pathlib import Path

from cgc.video.render_scene import render_scene_frame


def main() -> None:
    story_path = Path("output/story/1ORTExZg.json")
    data = json.loads(story_path.read_text(encoding="utf-8"))

    game_id = data["game_id"]
    scenes = data["scenes"]

    for scene in scenes:
        # For now, just render a couple to inspect layout
        if scene["type"] not in ("board", "text"):
            continue

        # Minimal shim: we only need raw dict fields that render_scene_frame uses.
        # Later we can add a Story.from_dict if needed.
        from cgc.domain.types import AlignmentInfo, AudioInfo, VisualInfo
        from cgc.domain.types import Scene as SceneModel

        s = SceneModel(
            index=scene["index"],
            id=scene["id"],
            type=scene["type"],
            role=scene.get("role"),
            ply=scene.get("ply"),
            display_lines=scene.get("display_lines", []),
            spoken_text=scene.get("spoken_text", ""),
            audio=AudioInfo(),  # not used here
            alignment=AlignmentInfo(),  # not used here
            visual=VisualInfo(
                highlight_mode=scene.get("visual", {}).get("highlight_mode")
            ),
            raw=scene.get("raw", {}),
        )

        out = render_scene_frame(s, game_id)
        print("wrote frame:", out)


if __name__ == "__main__":
    main()
