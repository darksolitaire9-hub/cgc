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
from cgc.voices import voice_label, voices_for_lang

cfg = PipelineConfig()

SAMPLE = (
    "Both knights crash forward with a check. "
    "This is the moment he starts pretending he is fine. "
    "A pawn to b4. Checkmate."
)

OUT_DIR = Path("voice_samples")
OUT_DIR.mkdir(exist_ok=True)

print(f"Current config voice: {cfg.kokoro_voice}\n")
pipeline = KPipeline(lang_code=cfg.kokoro_lang)

voices = voices_for_lang(cfg.kokoro_lang)

for voice in voices:
    grade = voice_label(voice)
    marker = "  <-- CURRENT" if voice == cfg.kokoro_voice else ""
    print(f"  {voice:<14} {grade}{marker}")
    for _, _, audio in pipeline(SAMPLE, voice=voice, speed=cfg.kokoro_speed):
        sf.write(OUT_DIR / f"{voice}.wav", audio, cfg.tts_sample_rate)
        break

items = []
for voice in voices:
    grade = voice_label(voice)
    active = (
        ' style="background:#fffbe6;border-left:3px solid #e6a817;padding-left:8px"'
        if voice == cfg.kokoro_voice
        else ""
    )
    tag = '  <b style="color:#b07800">* config</b>' if voice == cfg.kokoro_voice else ""
    items.append(
        f'<li{active}><code>{voice}</code> <span style="color:#888;font-size:.85em">'
        f"{grade}</span>{tag}"
        f'<br><audio controls src="{voice}.wav" style="width:100%;margin:.3rem 0 .7rem"></audio></li>'
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

(OUT_DIR / "index.html").write_text(html, encoding="utf-8")
print(f"\nPlayer -> voice_samples/index.html")
