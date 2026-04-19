from __future__ import annotations

import os
from pathlib import Path

os.environ["HF_HOME"] = str(Path(__file__).resolve().parent.parent / ".hf_cache")
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ.pop("HF_HUB_OFFLINE", None)

import soundfile as sf
from kokoro import KPipeline

from cgc.config import PipelineConfig
from cgc.voices import LanguageCode, voice_info, voice_label, voices_for_lang

SAMPLE = (
    "Both knights crash forward with a check. "
    "This is the moment he starts pretending he is fine. "
    "A pawn to b4. Checkmate."
)


def main() -> None:
    cfg = PipelineConfig()

    out_dir = Path("voice_samples")
    out_dir.mkdir(exist_ok=True)

    print(f"Current config voice: {cfg.kokoro_voice}\n")

    pipeline = KPipeline(
        lang_code=cfg.kokoro_lang,
        repo_id=cfg.kokoro_repo_id,
    )

    # Normalize lang to LanguageCode enum
    lang = LanguageCode(cfg.kokoro_lang)
    # voices_for_lang now returns a tuple of voice_id strings, e.g. ("af_bella", "am_fenrir", ...)
    voices = voices_for_lang(lang)

    # First pass: generate audio files
    for vid in voices:
        info = voice_info(vid)
        label = info.label if info is not None else voice_label(vid)
        tags = ", ".join(info.best_for) if info is not None and info.best_for else ""
        marker = "  <-- CURRENT" if vid == cfg.kokoro_voice else ""

        tag_str = f" [{tags}]" if tags else ""
        print(f"  {vid:<12} {label}{tag_str}{marker}")

        # KPipeline expects the string ID (e.g. "af_bella"), so we pass vid directly.
        for _, _, audio in pipeline(SAMPLE, voice=vid, speed=cfg.kokoro_speed):
            sf.write(out_dir / f"{vid}.wav", audio, cfg.tts_sample_rate)
            break

    # Second pass: build HTML
    items: list[str] = []
    for vid in voices:
        info = voice_info(vid)
        label = info.label if info is not None else voice_label(vid)
        tags = ", ".join(info.best_for) if info is not None and info.best_for else ""
        tags_html = (
            f'<span style="color:#555;font-size:.8em;margin-left:.35rem">[{tags}]</span>'
            if tags
            else ""
        )

        active = (
            ' style="background:#fffbe6;border-left:3px solid #e6a817;padding-left:8px"'
            if vid == cfg.kokoro_voice
            else ""
        )
        tag = (
            '  <b style="color:#b07800">* config</b>' if vid == cfg.kokoro_voice else ""
        )
        items.append(
            f"<li{active}><code>{vid}</code> "
            f'<span style="color:#888;font-size:.85em">{label}</span>'
            f"{tags_html}{tag}"
            f'<br><audio controls src="{vid}.wav" '
            f'style="width:100%;margin:.3rem 0 .7rem"></audio></li>'
        )

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>CGC Voice Sampler</title>
<style>body{{font-family:system-ui,sans-serif;max-width:560px;margin:2rem auto;
padding:0 1.5rem}}ul{{list-style:none;padding:0}}li{{padding:.5rem;
border-radius:6px;margin-bottom:.2rem}}audio{{width:100%}}
code{{background:#eee;padding:.1em .4em;border-radius:3px}}</style></head>
<body><h2>CGC Voice Sampler</h2>
<p style="color:#666;font-size:.9em">Active config: <code>{cfg.kokoro_voice}</code>
 | lang: <code>{cfg.kokoro_lang}</code> | speed: <code>{cfg.kokoro_speed}</code><br>
To change narrator: edit <code>cgc/config.py</code> kokoro_voice and re-run the pipeline.</p>
<ul>{"".join(items)}</ul></body></html>"""

    (out_dir / "index.html").write_text(html, encoding="utf-8")
    print("\nPlayer -> voice_samples/index.html")


if __name__ == "__main__":
    main()
