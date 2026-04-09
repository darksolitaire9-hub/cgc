from __future__ import annotations

from dataclasses import replace

from cgc.domain.types import AudioInfo, AudioManifest, Scene, SceneAudioRef, Story


def _scene_refs_by_id(manifest: AudioManifest) -> dict[str, SceneAudioRef]:
    return {ref.scene_id: ref for ref in manifest.scenes}


def apply_audio_manifest(story: Story, manifest: AudioManifest) -> Story:
    """
    Return a new Story where each Scene.audio is filled from the AudioManifest.

    - clip_path and duration come from SceneAudioRef.
    - start/end are computed by cumulative sum in the manifest, so the manifest
      remains the single source of timing truth for audio.
    """
    refs = _scene_refs_by_id(manifest)

    # Build a stable ordering of refs by scene index, so cumulative timing is deterministic.
    ordered_refs: list[SceneAudioRef] = sorted(manifest.scenes, key=lambda r: r.index)

    # Precompute start/end per scene_id.
    start_times: dict[str, float] = {}
    end_times: dict[str, float] = {}

    cursor = 0.0
    for ref in ordered_refs:
        dur = ref.duration or 0.0
        start_times[ref.scene_id] = cursor
        end_times[ref.scene_id] = cursor + dur
        cursor += dur

    new_scenes: list[Scene] = []
    for scene in story.scenes:
        ref = refs.get(scene.id)
        if ref is None:
            new_scenes.append(scene)
            continue

        start = start_times.get(scene.id)
        end = end_times.get(scene.id)

        new_audio = AudioInfo(
            clip_path=ref.clip_path,
            duration=ref.duration,
            start=start,
            end=end,
        )
        new_scene = replace(scene, audio=new_audio)
        new_scenes.append(new_scene)

    return Story(
        game_id=story.game_id,
        source_url=story.source_url,
        meta=story.meta,
        scenes=new_scenes,
    )
