import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import *  # noqa: E402,F403

UNITS = [("CPU", "Central", C_BLUE), ("GPU", "Graphics", C_YELLOW), ("TPU", "Tensor", C_GREEN),
         ("NPU", "Neural", C_PINK), ("LPU", "Language", C_ORANGE), ("WSE", "Wafer-Scale", C_RED),
         ("FPGA", "Field-Programmable", C_PURPLE), ("ASIC", "Application-Specific", C_GOLD),
         ("DPU", "Data", C_TEAL)]


class Hook(VoiceScene):
    def construct(self):
        facts = [
            ("4,000,000,000", "clock cycles per second, one CPU core", C_BLUE),
            ("1,000,000,000,000,000", "math operations per second, one H100 GPU", C_YELLOW),
            ("21 PB/s", "memory bandwidth, one Cerebras wafer", C_RED),
        ]
        rows = VGroup()
        for v, l, c in facts:
            rows.add(VGroup(T(v, size=54, color=c), T(l, size=24, color=C_GREY)).arrange(
                DOWN, buff=0.12))
        rows.arrange(DOWN, buff=0.6)
        with self.voiceover(
            "A single CPU core ticks about four billion times per second. An NVIDIA H100 GPU "
            "does about a thousand trillion math operations per second. A Cerebras wafer moves "
            "twenty one petabytes of data per second. Each of these is a processing unit, and "
            "each exists for a different reason."
        ) as vo:
            for r in rows:
                self.play(Write(r[0]), run_time=1.0)
                self.play(FadeIn(r[1], shift=UP * 0.1), run_time=0.5)
                self.wait(max(0.3, vo.duration / 3 - 2.3))

        tiles = VGroup()
        for abbr, word, col in UNITS:
            box = RoundedRectangle(width=3.6, height=1.5, corner_radius=0.1)
            box.set_stroke(col, 2).set_fill(col, 0.1)
            a = T(abbr, size=44, color=col)
            w = T(word, size=20, color=C_GREY)
            VGroup(a, w).arrange(DOWN, buff=0.1).move_to(box)
            tiles.add(VGroup(box, a, w))
        tiles.arrange_in_grid(3, 3, buff=(0.35, 0.3))
        with self.voiceover(
            "Here are nine of them, with real numbers: CPU, GPU, TPU, NPU, LPU, wafer-scale "
            "engines, FPGA, ASIC, and DPU."
        ) as vo:
            self.play(FadeOut(rows, shift=UP * 0.3), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(t, scale=0.85) for t in tiles], lag_ratio=0.25),
                      run_time=vo.duration - 1.2)

        with self.voiceover(
            "To compare them, we'll use one yardstick. When an AI model writes text, every new "
            "word requires reading every weight of the model from memory. So the speed limit is "
            "simple: memory bandwidth, divided by model size."
        ) as vo:
            self.play(tiles.animate.scale(0.45).to_edge(UP, buff=0.3).set_opacity(0.5),
                      run_time=1.0)
            rule = M(r"\text{tokens per second} \;\lesssim\; "
                     r"\frac{\text{memory bandwidth}}{\text{model size}}", 58)
            rule[0][16:31].set_color(C_BLUE)
            rule[0][32:].set_color(C_GOLD)
            rule.shift(DOWN * 0.2)
            self.wait(2.5)
            self.play(Write(rule), run_time=2.5)

        with self.voiceover(
            "Our test model: 8 billion parameters, stored at one byte each. That's 8 gigabytes "
            "to read for every single token."
        ) as vo:
            self.play(rule.animate.scale(0.6).next_to(tiles, DOWN, buff=0.5), run_time=0.8)
            blocks = VGroup(*[Square(0.8).set_stroke(C_GOLD, 1.5).set_fill(C_GOLD, 0.75)
                              for _ in range(8)]).arrange(RIGHT, buff=0.12)
            blocks.shift(DOWN * 1.3)
            eq = M(r"8 \text{ billion} \times 1 \text{ byte} = 8 \text{ GB per token}", 46)
            eq.next_to(blocks, DOWN, buff=0.45)
            gl = VGroup(*[T("1 GB", size=20, color=BLACK).move_to(b) for b in blocks])
            self.play(LaggedStart(*[GrowFromCenter(b) for b in blocks], lag_ratio=0.12),
                      FadeIn(gl), run_time=1.6)
            self.play(Write(eq), run_time=1.6)
        self.clear_all(run_time=0.6)
