import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import *  # noqa: E402,F403

# (name, memory bandwidth in GB/s, colour, tokens/s for the 8 GB yardstick or None)
BW = [
    ("NPU (laptop)", 135, C_PINK, "17"),
    ("CPU (EPYC 9654)", 460, C_BLUE, "57"),
    ("TPU v5e", 819, C_GREEN, "100"),
    ("GPU (H100)", 3_350, C_YELLOW, "420"),
    ("LPU (Groq, SRAM)", 80_000, C_ORANGE, None),
    ("WSE-3 (Cerebras, SRAM)", 21_000_000, C_RED, None),
]

JOBS = [
    ("CPU", "logic, control, anything unpredictable", C_BLUE),
    ("GPU", "massively parallel math: graphics, AI training and serving", C_YELLOW),
    ("TPU", "neural networks at data-center scale", C_GREEN),
    ("NPU", "AI on your phone or laptop, on battery", C_PINK),
    ("LPU / WSE", "very fast text generation from on-chip memory", C_ORANGE),
    ("FPGA", "custom, ultra-low-latency circuits you can rewire", C_PURPLE),
    ("ASIC", "one job, done as efficiently as possible", C_GOLD),
    ("DPU", "moving data: network, storage, security", C_TEAL),
]


class Summary(VoiceScene):
    def construct(self):
        title = T("Memory bandwidth decides text speed", size=36).to_edge(UP, buff=0.35)
        lo, hi = 2, 8  # log10 GB/s range drawn
        x0, width = -2.2, 8.4

        def x_of(gbs):
            return x0 + width * (np.log10(gbs) - lo) / (hi - lo)

        rows = VGroup()
        for i, (name, gbs, col, tps) in enumerate(BW):
            y = 1.9 - i * 0.82
            lab = T(name, size=24, color=col)
            lab.move_to([x0 - 0.25, y, 0], aligned_edge=RIGHT)
            bar = Rectangle(width=x_of(gbs) - x0, height=0.46).set_stroke(width=0).set_fill(col, 0.8)
            bar.move_to([x0, y, 0], aligned_edge=LEFT)
            val = gbs / 1000
            txt = (f"{gbs:,} GB/s" if gbs < 1000 else
                   f"{val:,.2f} TB/s" if val < 10 else
                   f"{val:,.0f} TB/s" if val < 1000 else f"{val / 1000:,.0f} PB/s")
            vt = T(txt, size=20, color=C_WHITE).next_to(bar, RIGHT, buff=0.15)
            tp = T(f"≈ {tps} tok/s" if tps else "", size=20, color=C_GREY).next_to(vt, RIGHT, 0.25)
            rows.add(VGroup(lab, bar, vt, tp))
        ticks = VGroup()
        for e, s in zip(range(lo, hi + 1), ["100 GB/s", "", "10 TB/s", "", "1 PB/s", "", "100 PB/s"]):
            x = x0 + width * (e - lo) / (hi - lo)
            ln = DashedLine([x, 2.35, 0], [x, -2.45, 0], color=C_GREY_D, stroke_width=1)
            ticks.add(ln)
            if s:
                ticks.add(T(s, size=16, color=C_GREY).move_to([x, -2.7, 0]))
        logn = T("log scale: each grid line = 10×", size=18, color=C_GREY).to_edge(DOWN, buff=0.3)

        with self.voiceover(
            "So here's the lineup by memory bandwidth, the number that decides how fast text "
            "comes out. From a laptop NPU at 135 gigabytes per second, to a Cerebras wafer at 21 "
            "petabytes per second. That's a range of over a hundred thousand times."
        ) as vo:
            self.play(Write(title), FadeIn(ticks), FadeIn(logn), run_time=1.2)
            for r in rows:
                self.play(FadeIn(r[0]), GrowFromEdge(r[1], LEFT), FadeIn(r[2]), FadeIn(r[3]),
                          run_time=min(1.2, (vo.duration - 2.0) / len(rows)))

        with self.voiceover(
            "And by job: the CPU for logic and control. The GPU for parallel math. The TPU and "
            "NPU for neural networks, in the data center and on device. The LPU and wafer-scale "
            "engines for very fast generation. FPGAs for custom low-latency circuits. ASICs for "
            "one job, done perfectly. And DPUs for moving data."
        ) as vo:
            self.play(FadeOut(VGroup(title, rows, ticks, logn)), run_time=0.6)
            table = VGroup()
            for abbr, job, col in JOBS:
                a = T(abbr, size=30, color=col)
                j = T(job, size=24, color=C_WHITE)
                table.add(VGroup(a, j))
            for row in table:
                row[0].move_to([-4.2, 0, 0], aligned_edge=RIGHT)
                row[1].move_to([-3.8, 0, 0], aligned_edge=LEFT)
            table.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
            for row in table:
                row[0].set_x(-4.2, direction=RIGHT)
                row[1].set_x(-3.8, direction=LEFT)
            table.move_to(DOWN * 0.1).shift(RIGHT * (0 - table.get_center()[0]))
            per = (vo.duration - 1.0) / len(table)
            for row in table:
                self.play(FadeIn(row, shift=RIGHT * 0.15), run_time=min(0.8, per * 0.6))
                self.wait(max(0.05, per * 0.4))

        with self.voiceover(
            "Every one of them is a different answer to the same question: where do you spend "
            "your transistors? On smart control, on raw math, or on memory right next to the math."
        ) as vo:
            self.play(FadeOut(table), run_time=0.6)
            q = T("Where do you spend your transistors?", size=44).shift(UP * 1.2)
            opts = VGroup(T("smart control", size=34, color=C_BLUE),
                          T("raw math", size=34, color=C_YELLOW),
                          T("memory next to the math", size=34, color=C_TEAL)).arrange(
                RIGHT, buff=0.8).next_to(q, DOWN, buff=0.9)
            self.play(Write(q), run_time=1.6)
            self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.2) for o in opts], lag_ratio=0.5),
                      run_time=max(1.5, self.remaining(vo) - 0.5))
        self.wait(1.0)
        self.clear_all(run_time=0.8)
