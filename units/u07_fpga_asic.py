import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import *  # noqa: E402,F403


def fpga_fabric(rng, cols=7, rows=5, cs=0.85):
    blocks, cells = VGroup(), {}
    for r in range(rows):
        for c in range(cols):
            is_dsp = c == 3
            col = C_YELLOW if is_dsp else C_PURPLE
            sq = Square(cs * 0.62).set_stroke(col, 1.5).set_fill(col, 0.25)
            lab = T("DSP" if is_dsp else "LUT", size=16, color=col).move_to(sq)
            g = VGroup(sq, lab).move_to([c * cs, -r * cs, 0])
            blocks.add(g)
            cells[(r, c)] = g
    return blocks, cells


def routing(cells, rng, n=14, color=C_PURPLE):
    keys = list(cells)
    wires = VGroup()
    for _ in range(n):
        a, b = rng.choice(len(keys), 2, replace=False)
        p, q = cells[keys[a]][0].get_center(), cells[keys[b]][0].get_center()
        mid = np.array([q[0], p[1], 0])
        wires.add(VMobject().set_points_as_corners([p, mid, q]).set_stroke(color, 2, 0.8))
    return wires


class FpgaAsic(VoiceScene):
    def construct(self):
        rng = np.random.default_rng(3)
        head = unit_header("FPGA", "Field-Programmable Gate Array", C_PURPLE, 7)
        blocks, cells = fpga_fabric(rng)
        fabric = VGroup(blocks)
        fabric.move_to(LEFT * 3.2 + DOWN * 0.3)
        w1 = routing(cells, rng, color=C_PURPLE)
        with self.voiceover(
            "The FPGA, or Field-Programmable Gate Array, is hardware you can rewire. It's a sea "
            "of small lookup tables, flip-flops and math blocks, with programmable wiring "
            "between them. Load a new configuration file, and the same chip becomes a different "
            "circuit."
        ) as vo:
            self.play(FadeIn(head, shift=RIGHT * 0.2), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(b, scale=0.8) for b in blocks], lag_ratio=0.02),
                      run_time=1.6)
            self.play(Create(w1), run_time=1.4)
            cfg = T("config A", size=24, color=C_PURPLE).next_to(fabric, UP, buff=0.25)
            self.play(FadeIn(cfg), run_time=0.4)
            self.wait(max(0.1, self.remaining(vo) - 2.6))
            w2 = routing(cells, np.random.default_rng(11), color=C_TEAL)
            cfg2 = T("config B: a different circuit", size=24, color=C_TEAL).move_to(cfg)
            self.play(ReplacementTransform(w1, w2), ReplacementTransform(cfg, cfg2),
                      run_time=1.4)

        board = spec_board([
            ("< 1 µs", "latency, e.g. high-frequency trading", C_PURPLE),
            ("networking", "packet processing at line rate", C_PURPLE),
            ("prototyping", "test a chip design before manufacturing", C_PURPLE),
            ("few hundred MHz", "clock speed (CPUs: about 4 GHz)", C_GREY),
        ], value_size=34, buff=0.26)
        board.move_to(RIGHT * 3.5 + DOWN * 0.3)
        with self.voiceover(
            "That gives you custom hardware without building a chip: sub-microsecond latency "
            "for high-frequency trading, network packet processing, and prototyping chips "
            "before they're manufactured. The cost: clock speeds of a few hundred megahertz, "
            "and much harder programming."
        ) as vo:
            reveal_specs(self, board, run_time=min(5.0, vo.duration - 0.6))

        # --- ASIC -------------------------------------------------------------
        with self.voiceover(
            "The ASIC, or Application-Specific Integrated Circuit, is the opposite: a chip that "
            "does exactly one thing, permanently. The TPU is an ASIC. So is a Bitcoin miner. An "
            "Antminer S21 computes 200 trillion hashes per second, something no CPU or GPU comes "
            "close to per watt."
        ) as vo:
            self.play(FadeOut(VGroup(fabric, w2, cfg2, board)), run_time=0.6)
            head2 = unit_header("ASIC", "Application-Specific Integrated Circuit", C_GOLD, 8)
            self.play(ReplacementTransform(head, head2), run_time=0.8)
            die = RoundedRectangle(width=5.6, height=2.6, corner_radius=0.1)
            die.set_stroke(C_GOLD, 2).set_fill("#0b0c0f", 1)
            stages = VGroup(*[Rectangle(width=0.5, height=1.4).set_stroke(C_GOLD, 1.2)
                              .set_fill(C_GOLD, 0.35) for _ in range(8)]).arrange(RIGHT, buff=0.12)
            stages.move_to(die)
            arrows = VGroup(*[Arrow(stages[i].get_right(), stages[i + 1].get_left(), buff=0.0,
                                    stroke_width=2, max_tip_length_to_length_ratio=0.5,
                                    color=C_GOLD) for i in range(7)])
            asic = VGroup(die, stages, arrows).move_to(LEFT * 3.0 + UP * 0.4)
            only = T("one fixed pipeline: SHA-256, nothing else", size=22, color=C_GOLD)
            only.next_to(asic, DOWN, buff=0.25)
            self.play(FadeIn(die), LaggedStart(*[FadeIn(s) for s in stages], lag_ratio=0.1),
                      FadeIn(arrows), FadeIn(only), run_time=1.6)
            tpu = T("TPU = an ASIC for matrix math", size=24, color=C_GREEN)
            tpu.next_to(only, DOWN, buff=0.35)
            self.play(FadeIn(tpu), run_time=0.6)
            # pulse data through the pipeline
            for _ in range(2):
                self.play(LaggedStart(*[s.animate.set_fill(C_GOLD, 0.9) for s in stages],
                                      lag_ratio=0.15), run_time=0.7)
                self.play(stages.animate.set_fill(C_GOLD, 0.35), run_time=0.3)
            big = VGroup(T("200 TH/s", size=60, color=C_GOLD),
                         T("200 trillion hashes per second", size=20, color=C_GREY),
                         T("Antminer S21 · 3,500 W", size=20, color=C_GREY)
                         ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            big.move_to(RIGHT * 3.6 + UP * 1.3)
            self.wait(max(0.1, self.remaining(vo) - 1.4))
            self.play(Write(big[0]), FadeIn(big[1:]), run_time=1.2)

        with self.voiceover(
            "The trade-off is cost and time. A cutting-edge ASIC can cost tens of millions of "
            "dollars and years to design, and if the algorithm changes, the chip is obsolete."
        ) as vo:
            cost = spec_board([
                ("$10M+", "to design a cutting-edge chip", C_RED),
                ("years", "from design to silicon", C_RED),
                ("fixed", "algorithm changes → obsolete", C_RED),
            ], value_size=34, buff=0.24)
            cost.next_to(big, DOWN, buff=0.5).align_to(big, LEFT)
            reveal_specs(self, cost, run_time=min(3.0, vo.duration - 0.6))
        self.clear_all(run_time=0.6)
