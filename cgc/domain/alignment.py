from __future__ import annotations

from dataclasses import replace

from cgc.domain.types import AlignmentManifest, Scene, SceneAlignmentRef, Story


def _alignment_refs_by_id(manifest: AlignmentManifest) -> dict[str, SceneAlignmentRef]:
    return {ref.scene_id: ref for ref in manifest.scenes}


def apply_alignment_manifest(story: Story, manifest: AlignmentManifest) -> Story:
    """
    Return a new Story where each Scene.alignment.words is filled from the
    AlignmentManifest. Does not change audio or other fields.
    """
    refs = _alignment_refs_by_id(manifest)

    new_scenes: list[Scene] = []
    for scene in story.scenes:
        ref = refs.get(scene.id)
        if ref is None:
            new_scenes.append(scene)
            continue

        # Keep the AlignmentInfo structure, only replace .words.
        new_alignment = replace(scene.alignment, words=list(ref.words))
        new_scene = replace(scene, alignment=new_alignment)
        new_scenes.append(new_scene)

    return Story(
        game_id=story.game_id,
        source_url=story.source_url,
        meta=story.meta,
        scenes=new_scenes,
    )
