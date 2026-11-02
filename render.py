#!/usr/bin/env python3
"""Render every chapter and stitch them into one narrated video with subtitles.

    export ELEVENLABS_API_KEY=...        # needed only for uncached narration
    python render.py                     # 1080p30 final render (all scenes)
    python render.py --draft             # fast 480p15 preview
    python render.py --only Intro        # re-render a subset, then re-assemble
    python render.py --project units     # the second video (every processing unit)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GPU_SCENES = [
    ("scenes/s01_intro.py", "Intro"),
    ("scenes/s02_cpu_gpu.py", "CpuVsGpu"),
    ("scenes/s03_anatomy.py", "Anatomy"),
    ("scenes/s04_roofline.py", "Roofline"),
    ("scenes/s05_llm.py", "LLMRecap"),
    ("scenes/s06_prefill_decode.py", "PrefillDecode"),
    ("scenes/s07_batching.py", "Batching"),
    ("scenes/s08_kv_cache.py", "KVCache"),
    ("scenes/s09_flash.py", "FlashAttention"),
    ("scenes/s10_outro.py", "Outro"),
]

UNITS_SCENES = [
    ("units/u01_hook.py", "Hook"),
    ("units/u02_cpu.py", "CPU"),
    ("units/u03_gpu.py", "GPU"),
    ("units/u04_tpu.py", "TPU"),
    ("units/u05_npu.py", "NPU"),
    ("units/u06_sram.py", "SRAMChips"),
    ("units/u07_fpga_asic.py", "FpgaAsic"),
    ("units/u08_dpu.py", "DPU"),
    ("units/u09_summary.py", "Summary"),
]
PROJECTS = {
    "gpu": dict(scenes=GPU_SCENES, out="gpu_llm_inference", script="SCRIPT.md"),
    "units": dict(scenes=UNITS_SCENES, out="processing_units", script="SCRIPT_units.md"),
}
SCENES = GPU_SCENES

TITLES = {
    "Intro": "Intro", "CpuVsGpu": "1. CPU vs GPU", "Anatomy": "2. Inside a GPU",
    "Roofline": "3. Feeding the beast", "LLMRecap": "4. What an LLM computes",
    "PrefillDecode": "5. Prefill and decode", "Batching": "6. Batching",
    "KVCache": "7. The KV cache", "FlashAttention": "8. FlashAttention",
    "Outro": "9. Thinking in bytes",
    "Hook": "Intro", "CPU": "CPU", "GPU": "GPU", "TPU": "TPU", "NPU": "NPU",
    "SRAMChips": "LPU & wafer-scale", "FpgaAsic": "FPGA & ASIC", "DPU": "DPU",
    "Summary": "The lineup",
}


def video_path(file: str, scene: str, folder: str) -> Path:
    return ROOT / "media" / "videos" / Path(file).stem / folder / f"{scene}.mp4"


def render(file: str, scene: str, draft: bool) -> tuple[str, int, str]:
    q = ["-ql"] if draft else ["-r", "1920,1080", "--frame_rate", "30"]
    cmd = [sys.executable, "-m", "manim", *q, "--media_dir", str(ROOT / "media"),
           "--disable_caching", str(ROOT / file), scene]
    for _ in range(2):  # parallel renders can race on manim's shared LaTeX cache; retry once
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if proc.returncode == 0:
            break
    return scene, proc.returncode, proc.stdout[-3000:] + proc.stderr[-3000:]


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def split_caption(text: str, max_words: int = 14):
    words = text.split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or (len(cur) >= 6 and w[-1] in ".,;:?!"):
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def duration(path: Path) -> float:
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)]).strip())


def assemble(folder: str, out: Path, script_name: str = "SCRIPT.md"):
    parts = [video_path(f, s, folder) for f, s in SCENES]
    missing = [p for p in parts if not p.exists()]
    if missing:
        print("missing renders:", *missing, sep="\n  ")
        return
    listing = ROOT / "media" / "concat.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in parts))

    # subtitles + script from the per-scene transcripts
    srt, script, offset, idx = [], ["# Narration script\n"], 0.0, 1
    for (f, s), p in zip(SCENES, parts):
        tr = json.loads((ROOT / "media" / "transcripts" / f"{s}.json").read_text())
        script.append(f"\n## {TITLES.get(s, s)}  ({srt_time(offset)[3:8]})\n\n")
        for seg in tr["segments"]:
            script.append(seg["text"] + "\n\n")
            chunks = split_caption(seg["text"])
            total_chars = sum(len(c) for c in chunks)
            t = offset + seg["start"]
            for c in chunks:
                d = seg["duration"] * len(c) / total_chars
                srt.append(f"{idx}\n{srt_time(t)} --> {srt_time(t + d)}\n{c}\n")
                idx += 1
                t += d
        offset += duration(p)
    srt_path = out.with_suffix(".srt")
    srt_path.write_text("\n".join(srt))
    (ROOT / script_name).write_text("".join(script))

    joined = ROOT / "media" / "joined.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(listing), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", str(joined)], check=True)
    # loudness-normalise the narration and attach soft subtitles
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(joined), "-i", str(srt_path),
                    "-map", "0:v", "-map", "0:a", "-map", "1:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
                    "-movflags", "+faststart", str(out)], check=True)
    print(f"wrote {out}  ({duration(out) / 60:.1f} min)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--project", choices=sorted(PROJECTS), default="gpu")
    args = ap.parse_args()
    global SCENES
    proj = PROJECTS[args.project]
    SCENES = proj["scenes"]

    todo = [(f, s) for f, s in SCENES if not args.only or s in args.only]
    if not args.no_render:
        with ThreadPoolExecutor(args.jobs) as ex:
            for scene, code, log in ex.map(lambda fs: render(*fs, args.draft), todo):
                print(f"[{'ok' if code == 0 else 'FAIL'}] {scene}")
                if code:
                    print(log)
    folder = "480p15" if args.draft else "1080p30"
    out = ROOT / "output" / (proj["out"] + ("_draft.mp4" if args.draft else ".mp4"))
    out.parent.mkdir(exist_ok=True)
    assemble(folder, out, proj["script"])


if __name__ == "__main__":
    main()
