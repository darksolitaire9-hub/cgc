from __future__ import annotations

from dataclasses import replace

from cgc.domain.types import AlignmentManifest, Scene, Story


def apply_alignment_manifest(story: Story, manifest: AlignmentManifest) -> Story:
    """Return a new Story with alignment.words filled from manifest."""
    ref_by_id = {(r.scene_id, r.index): r for r in manifest.scenes}

    new_scenes: list[Scene] = []
    for s in story.scenes:
        key = (s.id, s.index)
        ref = ref_by_id.get(key)
        if not ref:
            new_scenes.append(s)
            continue

        alignment = s.alignment
        alignment2 = replace(alignment, words=ref.words)
        new_scenes.append(replace(s, alignment=alignment2))

    return replace(story, scenes=new_scenes)
