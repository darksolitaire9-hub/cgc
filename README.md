# CGC – Chess Game Content

CGC turns a Lichess game + a YAML “story script” into a vertical chess short
(TikTok / Reels / Shorts) with:

- Hero-perspective board
- Kokoro TTS narration (`hexgrad/Kokoro-82M`, voice `af_nicole`, American English)
- Word-level karaoke subtitles (ASS hard-burned)
- Continuous perimeter progress bar
- Final-board outro with fade to black

---

## 1. First run

On a fresh machine you need to:

1) Install dependencies:

```bash
uv sync
```

2) (Optional but recommended) Preload Kokoro into the project-local HF cache:

```bash
uv run python -m cgc.tools.bootstrap_models
```

This downloads `hexgrad/Kokoro-82M` once into:

```text
cgc/.hf_cache/models--hexgrad--Kokoro-82M/...
```

After that, Hugging Face will reuse the cached model for all runs.

You can also skip the bootstrap step; the first `--no-fake-tts` pipeline run will trigger the same download automatically.

---

## 2. Requirements

- Python **3.11+**
- [`uv`](https://github.com/astral-sh/uv) installed
- [`ffmpeg`](https://ffmpeg.org/) available on your `PATH`
- Internet access at least once to download Kokoro (either via bootstrap or first real-TTS run)

Models and alignment assets are cached under `cgc/.hf_cache` via Hugging Face Hub.

---

## 3. Running the pipeline

All examples below use `--device cpu`.

### Fast run (fake TTS, fake alignment)

For quick visual checks:

```bash
uv run python -m cgc.pipeline scripts/game.yaml --device cpu
```

### Real TTS (Kokoro), fake alignment

Recommended normal run:

```bash
uv run python -m cgc.pipeline scripts/game.yaml --device cpu --no-fake-tts
```

- TTS: Kokoro KPipeline

  - Repo: `hexgrad/Kokoro-82M`
  - Voice: `af_nicole`
  - Lang: `"a"` (American English)
  - Speed: `1.0`

- Alignment: fake (no WhisperX).

### Real TTS + real WhisperX alignment (CPU)

When you want real word timings:

```bash
uv run python -m cgc.pipeline scripts/game.yaml --device cpu --no-fake-tts --no-fake-alignment
```

WhisperX models are cached under `cgc/.hf_cache/alignment_models`.

---

## 4. Story scripts (YAML) and scripts folder

To build a video, CGC needs:

- A **YAML story script** in the `scripts/` folder.

Flow:

```text
Lichess game URL → YAML story script → saved under scripts/ → pipeline → MP4
```

Example: `scripts/game.yaml`

```yaml
version: 1

source:
  type: lichess_url
  value: "https://lichess.org/anonymousGameId"

meta:
  voice: cinematic-bullet
  perspective: black

cards:
  - id: intro-1
    type: text
    duration: 2.8
    lines:
      - "They were outrated."
      - "The clock was against them."
      - "Nobody expected an upset."

  - id: opening-1
    type: board
    ply: 1
    role: opening
    duration: 2.1
    highlight:
      mode: last_move
    lines:
      - "A sharp opening choice."
      - "No room for quiet play."
      - "From move one, both sides were fighting."

  # ... midgame cards ...

  - id: finish-1
    type: board
    ply: 66
    role: finish
    duration: 2.1
    highlight:
      mode: last_move
    lines:
      - "One final precise move."
      - "And everything collapsed."

  - id: outro-1
    type: text
    duration: 2.8
    lines:
      - "One game."
      - "One chance."
      - "Complete domination."
```

Notes:

- Put your scripts under `scripts/`, e.g. `scripts/game.yaml`, `scripts/other_game.yaml`.
- `source.value` must be a full Lichess game URL (use your own game link).
- `meta.voice` is a style label (currently mapped to Kokoro’s `af_nicole` in code).
- `meta.perspective` is the hero side (`white` or `black`) and controls board flipping.
- `cards`:
  - `type: board` + `ply` show specific positions with optional `highlight.mode: last_move`.
  - `type: text` is narration-only:
    - `intro-*` ids show the **starting** position.
    - `outro-*` ids show the **final** board position.

To render a different script:

```bash
uv run python -m cgc.pipeline scripts/other_game.yaml --device cpu --no-fake-tts
```

---

## 5. Outputs

After a run you’ll see:

- Story JSON: `output/story/<game_id>.json`
- Frames: `output/frames/<game_id>_XX_<scene_id>.png`
- Subtitles (ASS): `output/subtitles/<game_id>.ass`
- Audio clips: `audio/clips/<game_id>/...`
- Merged audio: `audio/merged/<game_id>.wav`
- Final video: `output/video/<game_id>.mp4`