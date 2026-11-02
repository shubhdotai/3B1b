# GPUs & LLM Inference — a 3Blue1Brown-style explainer

A ~15 minute narrated, animated video on how a modern GPU is put together and how
large language model inference actually runs on it. It is built with
[Manim Community](https://www.manim.community/) in the visual style of 3Blue1Brown,
with narration synthesized by ElevenLabs.

**Final video:** `output/gpu_llm_inference.mp4` (1080p30, soft English subtitles)  
**Subtitles:** `output/gpu_llm_inference.srt` · **Narration script:** [`SCRIPT.md`](SCRIPT.md)

## Chapters

| # | Chapter | Main ideas |
|---|---------|-----------|
| 0 | Intro | Tokens stream one at a time; the surprise: memory, not math, is the bottleneck |
| 1 | CPU vs GPU | Latency vs throughput, professors vs a stadium of students, why matmul parallelises |
| 2 | Inside a GPU | H100 die: 132 SMs, 50 MB L2, 80 GB HBM; SM quadrants, CUDA & Tensor Cores; threads → warps → blocks → grid; memory hierarchy; ~300 FLOPs per byte |
| 3 | Feeding the beast | Arithmetic intensity, naive vs tiled matmul through shared memory, the roofline model |
| 4 | What an LLM computes | Tokens → vectors → attention/MLP layers → next-token distribution; it's all weights × vectors; 8B params = 16 GB |
| 5 | Prefill and decode | Prefill is compute-bound (matrix × matrix); decode is memory-bound (matrix × vector): 4.8 ms of loading vs 0.016 ms of math, ≈210 tokens/s ceiling |
| 6 | Batching | Load weights once, use for many users; throughput scales; continuous batching |
| 7 | The KV cache | Why keys/values are cached; 128 KB per token for Llama-3-8B; 64 GB for 64×8K contexts; PagedAttention |
| 8 | FlashAttention | Naive attention round-trips the N×N score grid through HBM; tiling + online softmax keep it on chip |
| 9 | Thinking in bytes | Quantization, speculative decoding, multi-GPU sharding; "the hard part is feeding it" |

Numbers are for an NVIDIA H100 SXM (989 dense BF16 TFLOP/s, 3.35 TB/s HBM3) and a
Llama-3-8B-shaped model (32 layers, 8 KV heads, head dim 128, BF16 weights).

## Layout

```
common/base.py    palette, text helpers, VoiceScene (narration-synced scene base)
common/gpu.py     reusable drawings: H100 die, SM, roofline plot
common/tts.py     ElevenLabs client with an on-disk cache (media/voice_cache)
scenes/s01..s10   one Manim scene per chapter; narration lives inline with the animation
render.py         renders all chapters in parallel, then concatenates, loudness-normalises,
                  and muxes subtitles; also regenerates SCRIPT.md
```

Each `with self.voiceover("..."):` block synthesizes (or loads from cache) the line,
starts the audio, runs the animations inside the block, then waits out whatever
narration remains — so visuals stay in sync even if the voice changes.

## Rebuilding

Requirements: Python 3.10+, `manim` (0.19+), ffmpeg, a LaTeX install (for `MathTex`),
and the CMU Serif font (`fonts-cmu` on Debian/Ubuntu).

```bash
export ELEVENLABS_API_KEY=...       # only needed for lines not already in media/voice_cache
python render.py --draft            # quick 480p15 preview -> output/gpu_llm_inference_draft.mp4
python render.py                    # final 1080p30        -> output/gpu_llm_inference.mp4
python render.py --only KVCache     # re-render one chapter, then re-assemble
```

The voice is set in `common/tts.py` (`ELEVENLABS_VOICE_ID` / `ELEVENLABS_MODEL_ID` env
vars override it). The API key is read from the environment and never stored in the repo.
