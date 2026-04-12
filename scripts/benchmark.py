# scripts/benchmark.py
from __future__ import annotations

import argparse
import time

from cgc.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", help="Path to storyboard YAML")
    args = parser.parse_args()

    for label, device in [("CPU", "cpu"), ("CUDA", "cuda")]:
        print(f"\n=== {label} RUN ===")
        t0 = time.perf_counter()
        run_pipeline(
            script_path=args.script,
            device=device,
            use_fake_tts=False,
            use_fake_alignment=False,
        )
        elapsed = time.perf_counter() - t0
        print(f"[benchmark] {label} total: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
