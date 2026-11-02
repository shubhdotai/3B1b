import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import *  # noqa: E402,F403


class GPU(VoiceScene):
    def construct(self):
        head = unit_header("GPU", "Graphics Processing Unit", C_YELLOW, 2)
        chip = gpu_chip(width=5.4, height=3.6)
        chip.move_to(LEFT * 3.0 + DOWN * 0.4)
        with self.voiceover(
            "The GPU: instead of a few smart cores, thousands of simple ones. The H100 has "
            "16,896 CUDA cores, grouped into 132 streaming multiprocessors, plus 528 Tensor "
            "Cores built only for matrix math."
        ) as vo:
            self.play(FadeIn(head, shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeIn(chip.die), FadeIn(chip.l2), FadeIn(chip.l2_label), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(g) for g in chip.gpcs], lag_ratio=0.12),
                      FadeIn(chip.hbm), run_time=1.6)
            lab = T("132 SMs · 16,896 cores · 528 Tensor Cores", size=24, color=C_YELLOW)
            lab.next_to(chip, DOWN, buff=0.25)
            self.play(LaggedStart(*[s.animate.set_fill(C_YELLOW, 0.8) for s in chip.sms],
                                  lag_ratio=0.005), Write(lab), run_time=1.6)
            self.play(chip.sms.animate.set_fill(C_YELLOW, 0.28), run_time=0.6)

        # warp lockstep + divergence
        warp = VGroup(*[Rectangle(width=0.1, height=0.7).set_stroke(C_YELLOW, 1)
                        .set_fill(C_YELLOW, 0.6) for _ in range(32)]).arrange(RIGHT, buff=0.03)
        warp.move_to(RIGHT * 4.3 + UP * 0.6)
        wl = T("32 threads, one instruction", size=22, color=C_YELLOW).next_to(warp, UP, 0.2)
        instr = Mono("FMA  a, b, c", size=22).next_to(warp, DOWN, 0.25)
        with self.voiceover(
            "Threads run in groups of 32 called warps, all executing the same instruction on "
            "different data. That's terrible for branchy code, where half the warp sits idle, "
            "but perfect for graphics and neural networks, where you do the same multiply-add "
            "millions of times."
        ) as vo:
            self.play(FadeIn(warp), FadeIn(wl), FadeIn(instr), run_time=1.0)
            for _ in range(2):
                self.play(warp.animate.shift(DOWN * 0.1), run_time=0.25)
                self.play(warp.animate.shift(UP * 0.1), run_time=0.25)
            branch = Mono("if (x > 0) ... else ...", size=22, color=C_RED)
            branch.move_to(instr)
            self.play(ReplacementTransform(instr, branch), run_time=0.6)
            self.play(*[w.animate.set_fill(C_GREY_D, 0.4).set_stroke(C_GREY_D)
                        for w in warp[1::2]], run_time=0.6)
            half = T("half the warp waits", size=22, color=C_RED).next_to(branch, DOWN, 0.2)
            self.play(FadeIn(half), run_time=0.5)
            self.wait(max(0.1, self.remaining(vo) - 2.4))
            instr2 = Mono("FMA  a, b, c", size=22).move_to(branch)
            self.play(ReplacementTransform(branch, instr2), FadeOut(half),
                      *[w.animate.set_fill(C_YELLOW, 0.6).set_stroke(C_YELLOW)
                        for w in warp[1::2]], run_time=0.8)
            good = T("same math, millions of times", size=22, color=C_GREEN)
            good.next_to(instr2, DOWN, 0.2)
            self.play(FadeIn(good), run_time=0.6)

        board = spec_board([
            ("≈ 990 TFLOP/s", "16-bit matrix math (dense)", C_YELLOW),
            ("80 GB", "HBM3 memory", C_BLUE),
            ("3.35 TB/s", "memory bandwidth", C_BLUE),
            ("700 W", "power", C_GREY),
        ])
        board.move_to(RIGHT * 3.5 + DOWN * 0.2)
        with self.voiceover(
            "The numbers: about 990 teraflops of 16-bit matrix math, 80 gigabytes of high "
            "bandwidth memory at 3.35 terabytes per second, and 700 watts."
        ) as vo:
            self.play(FadeOut(VGroup(warp, wl, instr2, good)), run_time=0.5)
            reveal_specs(self, board, run_time=min(4.0, vo.duration - 0.8))

        with self.voiceover(
            "Yardstick: 3.35 terabytes per second over 8 gigabytes is about 420 tokens per "
            "second. Seven times the CPU, and mostly because of memory, not math."
        ) as vo:
            self.play(VGroup(chip, lab).animate.scale(0.75).shift(UP * 0.8),
                      board.animate.scale(0.8).shift(UP * 0.6), run_time=0.6)
            ys = yardstick(r"3{,}350\ \text{GB/s}", r"420\ \text{tokens/s}")
            ys.to_edge(DOWN, buff=0.3)
            self.play(FadeIn(ys, shift=UP * 0.2), run_time=1.2)
            x7 = T("7× the CPU", size=28, color=C_YELLOW).next_to(ys, RIGHT, buff=0.4)
            self.play(FadeIn(x7, shift=LEFT * 0.2), run_time=0.8)
        self.clear_all(run_time=0.6)
