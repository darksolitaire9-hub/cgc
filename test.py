from cgc.domain.timeline import (
    assign_scene_timing,
    compute_total_duration,
    validate_scene_durations,
    validate_scene_order,
    validate_word_windows,
)
from cgc.pipeline import run_pipeline


def main() -> None:
    script_path = "examples/1ORTExZg.yaml"

    story = run_pipeline(script_path)

    # These are already called inside run_pipeline, but you can re-run them here
    # if you want explicit tests.
    validate_scene_order(story)
    validate_scene_durations(story)
    validate_word_windows(story)
    story = assign_scene_timing(story)
    total = compute_total_duration(story)

    print("Total duration (test):", total)


if __name__ == "__main__":
    main()
