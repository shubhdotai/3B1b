import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import *  # noqa: E402,F403


class SRAMChips(VoiceScene):
    def construct(self):
        head = unit_header("LPU", "Language Processing Unit · Groq", C_ORANGE, 5)
        die = RoundedRectangle(width=5.0, height=3.4, corner_radius=0.1)
        die.set_stroke(C_ORANGE, 2).set_fill("#0b0c0f", 1)
        tiles = VGroup()
        for i in range(10):
            col = C_TEAL if i % 2 == 0 else C_ORANGE
            r = Rectangle(width=0.42, height=3.0).set_stroke(col, 1).set_fill(col, 0.35 if
                                                                           col == C_TEAL else 0.5)
            tiles.add(r)
        tiles.arrange(RIGHT, buff=0.05).move_to(die)
        lpu = VGroup(die, tiles).move_to(LEFT * 3.2 + DOWN * 0.2)
        leg = VGroup(VGroup(Square(0.22).set_fill(C_TEAL, 0.6).set_stroke(C_TEAL, 1),
                            T("on-chip SRAM", size=20, color=C_TEAL)).arrange(RIGHT, buff=0.12),
                     VGroup(Square(0.22).set_fill(C_ORANGE, 0.6).set_stroke(C_ORANGE, 1),
                            T("compute", size=20, color=C_ORANGE)).arrange(RIGHT, buff=0.12)
                     ).arrange(RIGHT, buff=0.5).next_to(lpu, DOWN, buff=0.25)
        no_hbm = T("no external memory", size=24, color=C_GREY).next_to(lpu, UP, buff=0.2)
        with self.voiceover(
            "The LPU, Groq's Language Processing Unit, attacks the memory problem head on. It "
            "has no external memory at all. Each chip holds 230 megabytes of on-chip SRAM, "
            "readable at 80 terabytes per second: about 24 times the H100's memory bandwidth."
        ) as vo:
            self.play(FadeIn(head, shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeIn(die), LaggedStart(*[GrowFromEdge(t, DOWN) for t in tiles],
                                               lag_ratio=0.08), FadeIn(leg), run_time=1.6)
            self.play(FadeIn(no_hbm), run_time=0.6)
            # bandwidth bars
            axis_l = 5.4
            h100 = Rectangle(width=axis_l * 3.35 / 80, height=0.5).set_stroke(width=0).set_fill(
                C_BLUE, 0.85)
            lpu_b = Rectangle(width=axis_l, height=0.5).set_stroke(width=0).set_fill(C_TEAL, 0.85)
            bars = VGroup(h100, lpu_b).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
            bars.move_to(RIGHT * 3.6 + UP * 0.4)
            hl = T("H100 HBM · 3.35 TB/s", size=22, color=C_BLUE).next_to(h100, UP, 0.1,
                                                                         aligned_edge=LEFT)
            ll = T("LPU SRAM · 80 TB/s", size=22, color=C_TEAL).next_to(lpu_b, UP, 0.1,
                                                                       aligned_edge=LEFT)
            self.wait(max(0.1, self.remaining(vo) - 3.6))
            self.play(GrowFromEdge(h100, LEFT), FadeIn(hl), run_time=0.8)
            self.play(GrowFromEdge(lpu_b, LEFT), FadeIn(ll), run_time=1.2)
            x24 = T("≈ 24×", size=40, color=C_TEAL).next_to(bars, DOWN, buff=0.35)
            self.play(FadeIn(x24, scale=1.3), run_time=0.6)
            bw_view = VGroup(bars, hl, ll, x24)

        with self.voiceover(
            "The catch: 230 megabytes is tiny. A 70 billion parameter model needs about 300 of "
            "these chips, chained together, with a compiler scheduling every data movement "
            "ahead of time, down to the clock cycle."
        ) as vo:
            self.play(FadeOut(bw_view), run_time=0.5)
            calc = M(r"\frac{70\ \text{GB}}{230\ \text{MB}} \approx 300 \text{ chips}", 44)
            calc.move_to(RIGHT * 3.5 + UP * 1.6)
            self.play(Write(calc), run_time=1.4)
            chips = VGroup(*[Square(0.16).set_stroke(C_ORANGE, 0.8).set_fill(C_ORANGE, 0.5)
                             for _ in range(300)]).arrange_in_grid(12, 25, buff=0.04)
            chips.next_to(calc, DOWN, buff=0.4)
            self.play(LaggedStart(*[FadeIn(c) for c in chips], lag_ratio=0.004), run_time=1.8)
            sched = T("every move planned by the compiler", size=22, color=C_GREY)
            sched.next_to(chips, DOWN, buff=0.25)
            self.play(FadeIn(sched), run_time=0.6)

        # --- Cerebras wafer-scale --------------------------------------------
        with self.voiceover(
            "Cerebras takes the idea to the extreme. Instead of cutting a silicon wafer into "
            "hundreds of chips, it keeps the whole wafer as one chip: 46,225 square millimeters, "
            "4 trillion transistors, 900,000 cores, and 44 gigabytes of SRAM at 21 petabytes per "
            "second."
        ) as vo:
            self.play(FadeOut(VGroup(lpu, leg, no_hbm, calc, chips, sched)), run_time=0.6)
            head2 = unit_header("WSE", "Wafer-Scale Engine · Cerebras", C_RED, 6)
            self.play(ReplacementTransform(head, head2), run_time=0.8)
            mm = 0.018  # scene units per millimetre
            wafer = Circle(radius=150 * mm).set_stroke(C_GREY, 2).set_fill("#121418", 1)
            wse = Square(215 * mm).set_stroke(C_RED, 2.5).set_fill(C_RED, 0.12)
            grid = VGroup(*[Square(215 * mm / 7 * 0.94).set_stroke(C_RED, 0.8, opacity=0.6)
                            .set_fill(opacity=0) for _ in range(49)]).arrange_in_grid(
                7, 7, buff=215 * mm / 7 * 0.06)
            grid.move_to(wse)
            wafer_g = VGroup(wafer, wse, grid).move_to(LEFT * 3.3 + DOWN * 0.4)
            h100_die = Square(np.sqrt(814) * mm).set_stroke(C_YELLOW, 2).set_fill(C_YELLOW, 0.5)
            h100_die.next_to(wafer_g, RIGHT, buff=0.4).align_to(wafer_g, DOWN)
            hl = T("H100 die,\nsame scale", size=18, color=C_YELLOW).next_to(h100_die, UP, 0.12)
            self.play(FadeIn(wafer), run_time=0.6)
            self.play(Create(wse), LaggedStart(*[FadeIn(g) for g in grid], lag_ratio=0.02),
                      run_time=1.4)
            self.play(FadeIn(h100_die), FadeIn(hl), run_time=0.8)
            board = spec_board([
                ("46,225 mm²", "one chip, the whole wafer", C_RED),
                ("4 trillion", "transistors", C_WHITE),
                ("900,000", "cores", C_ORANGE),
                ("44 GB", "on-chip SRAM", C_TEAL),
                ("21 PB/s", "memory bandwidth", C_TEAL),
            ], value_size=36, buff=0.24)
            board.move_to(RIGHT * 4.2 + DOWN * 0.3)
            reveal_specs(self, board, run_time=max(2.0, self.remaining(vo) - 0.6))

        with self.voiceover(
            "The payoff is speed. Cerebras has reported around 1,800 tokens per second on "
            "Llama 3.1 8B, several times what a single GPU manages."
        ) as vo:
            res = VGroup(T("≈ 1,800 tokens/s", size=46, color=C_RED),
                         T("reported by Cerebras · Llama 3.1 8B", size=20, color=C_GREY)
                         ).arrange(DOWN, buff=0.1)
            box = SurroundingRectangle(res, color=C_RED, buff=0.22, corner_radius=0.1)
            box.set_fill(BLACK, 0.85)
            card = VGroup(box, res).to_edge(DOWN, buff=0.3).shift(LEFT * 2.6)
            self.play(VGroup(wafer_g, h100_die, hl).animate.scale(0.72).shift(UP * 0.75),
                      run_time=0.6)
            self.play(FadeIn(card, shift=UP * 0.2), run_time=1.0)
        self.clear_all(run_time=0.6)
