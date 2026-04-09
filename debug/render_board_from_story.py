import json
from pathlib import Path


from cgc.video.render_board import render_board_image


def main() -> None:
    story_path = Path("output/story/1ORTExZg.json")
    data = json.loads(story_path.read_text(encoding="utf-8"))

    # Find first board scene
    board_scene = next(s for s in data["scenes"] if s["type"] == "board")

    fen = board_scene["raw"]["fen"]
    last_move_uci = board_scene["raw"].get("last_move_uci")

    out = render_board_image(
        fen=fen,
        last_move_uci=last_move_uci,
        size=720,
        out_path="output/frames/1ORTExZg_opening-1.png",
    )
    print("wrote frame:", out)


if __name__ == "__main__":
    main()
