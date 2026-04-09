from __future__ import annotations

from dataclasses import replace

from cgc.domain.types import AudioManifest, Scene, Story


def apply_audio_manifest(story: Story, manifest: AudioManifest) -> Story:
    """Return a new Story with audio.clip_path and duration filled from manifest."""
    ref_by_id = {(r.scene_id, r.index): r for r in manifest.scenes}

    new_scenes: list[Scene] = []
    for s in story.scenes:
        key = (s.id, s.index)
        ref = ref_by_id.get(key)
        if not ref:
            new_scenes.append(s)
            continue

        audio = s.audio
        audio2 = replace(
            audio,
            clip_path=ref.clip_path,
            duration=ref.duration,
        )
        new_scenes.append(replace(s, audio=audio2))

    return replace(story, scenes=new_scenes)
