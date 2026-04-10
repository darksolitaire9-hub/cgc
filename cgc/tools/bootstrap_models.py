from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download

KOKORO_REPO_ID = "hexgrad/Kokoro-82M"


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    hf_home = project_root / ".hf_cache"
    print(f"[bootstrap] HF_HOME={hf_home}")
    hf_home.mkdir(parents=True, exist_ok=True)

    print(f"[bootstrap] downloading Kokoro model {KOKORO_REPO_ID!r}...")
    local_repo = snapshot_download(
        repo_id=KOKORO_REPO_ID,
        cache_dir=str(hf_home),
        local_files_only=False,
    )
    print(f"[bootstrap] Kokoro cached at {local_repo}")
    print("[bootstrap] done. You can now run the pipeline offline.")


if __name__ == "__main__":
    main()
