import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import *  # noqa: E402,F403


def ccd(w=1.35, h=1.0):
    frame = RoundedRectangle(width=w, height=h, corner_radius=0.05)
    frame.set_stroke(C_BLUE, 1.5).set_fill("#0d1418", 1)
    cores = VGroup(*[Square(0.2).set_stroke(C_BLUE, 1).set_fill(C_BLUE, 0.45) for _ in range(8)])
    cores.arrange_in_grid(2, 4, buff=0.06).move_to(frame).shift(UP * 0.13)
    l3 = Rectangle(width=w * 0.85, height=0.18).set_stroke(C_TEAL, 1).set_fill(C_TEAL, 0.35)
    l3.next_to(cores, DOWN, buff=0.08)
    return VGroup(frame, cores, l3)


class CPU(VoiceScene):
    def construct(self):
        head = unit_header("CPU", "Central Processing Unit", C_BLUE, 1)
        pkg = RoundedRectangle(width=6.4, height=4.6, corner_radius=0.15)
        pkg.set_stroke(C_GREY, 2).set_fill("#0b0c0f", 1)
        io = labeled_box("I/O die", 2.0, 3.6, color=C_GREY, size=22, fill_opacity=0.15)
        left = VGroup(*[ccd() for _ in range(6)]).arrange_in_grid(3, 2, buff=0.12)
        right = VGroup(*[ccd() for _ in range(6)]).arrange_in_grid(3, 2, buff=0.12)
        layout = VGroup(left, io, right).arrange(RIGHT, buff=0.18)
        layout.scale_to_fit_width(6.0)
        cpu = VGroup(pkg, layout.move_to(pkg)).move_to(LEFT * 2.9 + DOWN * 0.35)
        ccds = VGroup(*left, *right)

        with self.voiceover(
            "The CPU: a few dozen big, smart cores. A server chip like AMD's EPYC 9654 has "
            "96 of them: twelve chiplets of eight cores each, running at up to 3.7 gigahertz."
        ) as vo:
            self.play(FadeIn(head, shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeIn(pkg), FadeIn(io), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in ccds], lag_ratio=0.1),
                      run_time=2.0)
            lab = T("12 chiplets × 8 cores = 96 cores", size=26, color=C_BLUE)
            lab.next_to(cpu, DOWN, buff=0.25)
            self.play(Write(lab), run_time=1.2)

        # zoom on a single core
        core = VGroup()
        boxes = [("Branch predictor", C_PURPLE, 3.2, 0.55), ("Decode", C_PURPLE, 3.2, 0.45),
                 ("Out-of-order scheduler", C_PURPLE, 3.2, 0.75),
                 ("ALUs + vector units", C_YELLOW, 3.2, 0.55),
                 ("L1 / L2 cache", C_TEAL, 3.2, 0.7)]
        for name, col, w, h in boxes:
            core.add(labeled_box(name, w, h, color=col, size=20, fill_opacity=0.2))
        core.arrange(DOWN, buff=0.1)
        core_frame = SurroundingRectangle(core, color=C_BLUE, buff=0.18, corner_radius=0.1)
        core_t = T("one core", size=24, color=C_BLUE).next_to(core_frame, UP, buff=0.12)
        core_g = VGroup(core_frame, core, core_t).move_to(RIGHT * 2.7 + DOWN * 0.35)
        with self.voiceover(
            "Each core is built to finish one stream of instructions as fast as possible. It "
            "predicts which way branches will go, runs instructions out of order, and keeps 384 "
            "megabytes of cache close by. That makes it great at messy, unpredictable work: "
            "operating systems, databases, game logic, your browser."
        ) as vo:
            src = ccds[0][1][0]
            self.play(Indicate(src, color=C_WHITE, scale_factor=2), run_time=0.8)
            self.play(TransformFromCopy(src, core_frame), FadeIn(core_t), run_time=0.9)
            self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.1) for b in core], lag_ratio=0.3),
                      run_time=2.2)
            ctl = Brace(core[:3], RIGHT, color=C_PURPLE)
            ctl_t = T("most of the area:\ncontrol", size=20, color=C_PURPLE).next_to(ctl, RIGHT, 0.1)
            self.play(GrowFromCenter(ctl), FadeIn(ctl_t), run_time=1.0)
            uses = T("OS · databases · game logic · browsers", size=24, color=C_GREY)
            uses.next_to(lab, DOWN, buff=0.15)
            self.wait(max(0.1, self.remaining(vo) - 2.0))
            self.play(FadeIn(uses), run_time=0.8)

        board = spec_board([
            ("96 cores", "up to 3.7 GHz", C_BLUE),
            ("≈ 10 TFLOP/s", "32-bit math, all cores", C_YELLOW),
            ("460 GB/s", "12 channels of DDR5 memory", C_BLUE),
            ("384 MB", "L3 cache", C_TEAL),
            ("360 W", "power", C_GREY),
        ])
        board.move_to(RIGHT * 3.5 + DOWN * 0.3)
        with self.voiceover(
            "For raw math it's limited: about ten teraflops across all 96 cores, roughly a "
            "hundred times less than a GPU's matrix units. Its memory is twelve channels of "
            "DDR5, about 460 gigabytes per second."
        ) as vo:
            self.play(FadeOut(VGroup(core_g, ctl, ctl_t)), run_time=0.6)
            reveal_specs(self, board, run_time=min(4.0, vo.duration - 1.0))

        with self.voiceover(
            "Divide by our 8 gigabyte model, and you get about 57 tokens per second, at best. "
            "Usable, but not fast."
        ) as vo:
            ys = yardstick(r"460\ \text{GB/s}", r"57\ \text{tokens/s}", color=C_BLUE)
            ys.to_edge(DOWN, buff=0.3)
            self.play(FadeOut(uses), VGroup(cpu, lab).animate.scale(0.75).shift(UP * 0.8),
                      board.animate.scale(0.8).shift(UP * 0.6), run_time=0.6)
            self.play(FadeIn(ys, shift=UP * 0.2), run_time=1.2)
        self.clear_all(run_time=0.6)
