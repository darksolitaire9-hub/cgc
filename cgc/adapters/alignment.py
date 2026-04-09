from __future__ import annotations

from cgc.domain.types import AlignmentManifest, SceneAlignmentRef, Story, WordTiming


def build_fake_alignment_manifest(story: Story) -> AlignmentManifest:
    """
    Stub alignment: give each scene one fake word spanning its audio window.
    This lets us wire subtitles end-to-end before WhisperX.
    """
    scene_refs: list[SceneAlignmentRef] = []

    for s in story.scenes:
        if s.audio.start is None or s.audio.end is None:
            continue

        mid = (s.audio.start + s.audio.end) / 2.0
        word = WordTiming(
            word=(s.spoken_text.split()[:1] or ["..."])[0],
            start=s.audio.start,
            end=mid,
        )
        scene_refs.append(
            SceneAlignmentRef(
                scene_id=s.id,
                index=s.index,
                words=[word],
            )
        )

    return AlignmentManifest(
        game_id=story.game_id,
        scenes=scene_refs,
    )
