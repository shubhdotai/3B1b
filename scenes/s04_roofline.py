import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403

N = 6
CS = 0.42


def matmul_layout():
    rng = np.random.default_rng(7)
    A = cell_grid(N, N, CS, C_BLUE, rng.uniform(0.15, 0.6, (N, N)))
    B = cell_grid(N, N, CS, C_PINK, rng.uniform(0.15, 0.6, (N, N)))
    Cg = cell_grid(N, N, CS, C_YELLOW, np.zeros((N, N)), min_opacity=0.03)
    Cg.move_to(RIGHT * 0.2 + DOWN * 1.3)
    A.next_to(Cg, LEFT, buff=0.35)
    B.next_to(Cg, UP, buff=0.35)
    la = M("A", 36, C_BLUE).next_to(A, LEFT, buff=0.2)
    lb = M("B", 36, C_PINK).next_to(B, LEFT, buff=0.2)
    lc = M("C", 36, C_YELLOW).next_to(Cg, RIGHT, buff=0.2)
    return A, B, Cg, VGroup(la, lb, lc)


class Roofline(VoiceScene):
    def construct(self):
        self.chapter_card(3, "Feeding the beast")

        with self.voiceover(
            "This ratio, operations performed per byte moved, is called arithmetic "
            "intensity, and it's the single most useful number for thinking about GPU "
            "performance."
        ) as vo:
            name = T("Arithmetic intensity", size=54, color=C_WHITE)
            frac = M(r"= \frac{\text{FLOPs performed}}{\text{bytes moved from memory}}", 50)
            frac[0][1:15].set_color(C_YELLOW)
            frac[0][16:].set_color(C_BLUE)
            grp = VGroup(name, frac).arrange(DOWN, buff=0.5)
            self.play(Write(name), run_time=1.4)
            self.play(Write(frac), run_time=2.0)
            self.wait(self.remaining(vo) - 1.0)
            self.play(grp.animate.scale(0.5).to_corner(UL, buff=0.3), run_time=1.0)

        # --- Naive matmul --------------------------------------------------
        A, B, Cg, labs = matmul_layout()
        counter_t = T("values read from HBM:", size=26, color=C_BLUE)
        counter = Integer(0, font_size=40, color=C_BLUE)
        cgrp = VGroup(counter_t, counter).arrange(DOWN, buff=0.2)
        cgrp.move_to(RIGHT * 4.9 + DOWN * 0.3)
        with self.voiceover(
            "Take matrix multiplication again. If every output entry naively went back "
            "to main memory to fetch its own row and its own column, the same numbers "
            "would be fetched over and over, and the intensity would be terrible."
        ) as vo:
            self.play(FadeIn(VGroup(A, B, Cg, labs)), FadeIn(cgrp), run_time=1.2)
            reads = 0
            for (i, j) in [(0, 0), (0, 1), (0, 2)]:
                row = VGroup(*A.cells[i])
                col = VGroup(*[B.cells[r][j] for r in range(N)])
                rect_r = SurroundingRectangle(row, color=C_WHITE, buff=0.02)
                rect_c = SurroundingRectangle(col, color=C_WHITE, buff=0.02)
                copies = VGroup(row.copy(), col.copy())
                reads += 2 * N
                self.play(Create(rect_r), Create(rect_c),
                          copies.animate.set_fill(C_BLUE, 0.9), run_time=0.6)
                self.play(*[m.animate.move_to(Cg.cells[i][j]).scale(0.15)
                            for m in copies],
                          ChangeDecimalToValue(counter, reads), run_time=0.7)
                self.drop(copies)
                self.play(Cg.cells[i][j].animate.set_fill(C_YELLOW, 0.8),
                          FadeOut(rect_r), FadeOut(rect_c), run_time=0.4)
            again = T("same row, fetched again!", size=26, color=C_RED)
            again.next_to(A, DOWN, buff=0.25)
            self.play(Indicate(VGroup(*A.cells[0]), color=C_RED), FadeIn(again), run_time=1.0)
            # fast forward the rest
            rest = [Cg.cells[i][j] for i in range(N) for j in range(N)
                    if not (i == 0 and j < 3)]
            self.play(LaggedStart(*[c.animate.set_fill(C_YELLOW, 0.8) for c in rest],
                                  lag_ratio=0.03),
                      ChangeDecimalToValue(counter, 2 * N * N * N),
                      run_time=max(1.0, self.remaining(vo) - 1.4))
            uniq = T(f"for only {2 * N * N} distinct numbers", size=22, color=C_GREY)
            uniq.next_to(cgrp, DOWN, buff=0.2)
            self.play(FadeIn(uniq), run_time=0.6)

        # --- Tiling --------------------------------------------------------
        smem = labeled_box("Shared memory", 3.0, 1.0, color=C_TEAL, size=26,
                           fill_opacity=0.15)
        smem.move_to(RIGHT * 4.9 + UP * 2.1)
        with self.voiceover(
            "Instead, well-written GPU code uses a technique called tiling. A thread block "
            "loads one square tile of each input matrix into the fast shared memory, just "
            "once. Then every thread in the block reuses those values many times, "
            "accumulating partial results for a whole tile of the output. Then it slides "
            "on to the next pair of tiles."
        ) as vo:
            self.play(FadeOut(again), FadeOut(uniq), Cg.animate.set_fill(C_YELLOW, 0.03),
                      ChangeDecimalToValue(counter, 0), FadeIn(smem), run_time=1.0)
            h = N // 2

            def tile(G, ti, tj):
                return VGroup(*[G.cells[r][c] for r in range(ti * h, ti * h + h)
                                for c in range(tj * h, tj * h + h)])

            reads = 0
            order = [(0, 0), (0, 1), (1, 0), (1, 1)]
            slow = 2  # animate the first C tiles in detail
            for n, (ti, tj) in enumerate(order):
                ct = tile(Cg, ti, tj)
                ct_rect = SurroundingRectangle(ct, color=C_YELLOW, buff=0.03)
                for k in range(2):
                    at, bt = tile(A, ti, k), tile(B, k, tj)
                    ra = SurroundingRectangle(at, color=C_WHITE, buff=0.03)
                    rb = SurroundingRectangle(bt, color=C_WHITE, buff=0.03)
                    reads += 2 * h * h
                    ca, cb = at.copy(), bt.copy()
                    rt = 0.55 if n < slow else 0.25
                    self.play(Create(ra), Create(rb), *([Create(ct_rect)] if k == 0 else []),
                              run_time=rt)
                    self.play(ca.animate.scale(0.5).move_to(smem.box.get_center() + LEFT * 0.6),
                              cb.animate.scale(0.5).move_to(smem.box.get_center() + RIGHT * 0.6),
                              ChangeDecimalToValue(counter, reads), run_time=rt * 1.2)
                    self.play(*[c.animate.set_fill(C_YELLOW, 0.35 + 0.45 * k) for c in ct],
                              Indicate(smem.box, color=C_TEAL, scale_factor=1.05),
                              run_time=rt * 1.2)
                    self.play(FadeOut(VGroup(ca, cb, ra, rb)), run_time=rt * 0.6)
                self.play(FadeOut(ct_rect), run_time=0.2)
            cmp = T(f"{reads} reads instead of {2 * N ** 3}", size=24, color=C_TEAL)
            cmp.next_to(cgrp, DOWN, buff=0.25)
            self.play(Write(cmp), run_time=0.8)

        with self.voiceover(
            "The bigger the tile, the more reuse you get out of every byte. For an n by n "
            "tile, you move on the order of n squared numbers, but do on the order of n "
            "cubed operations. So the intensity grows with the size of the tile."
        ) as vo:
            self.play(FadeOut(VGroup(A, B, Cg, labs, cgrp, cmp, smem)), run_time=0.8)
            sq = Square(2.2).set_stroke(C_TEAL, 3).set_fill(C_TEAL, 0.2).shift(LEFT * 4 + DOWN * 0.3)
            nl = M("n", 40).next_to(sq, DOWN, buff=0.15)
            nl2 = M("n", 40).next_to(sq, LEFT, buff=0.15)
            self.play(Create(sq), FadeIn(nl), FadeIn(nl2), run_time=1.0)
            l1 = M(r"\text{bytes moved} \;\sim\; n^2", 46, C_BLUE)
            l2 = M(r"\text{operations} \;\sim\; n^3", 46, C_YELLOW)
            l3 = M(r"\text{intensity} \;\sim\; \frac{n^3}{n^2} = n", 46, C_WHITE)
            lines = VGroup(l1, l2, l3).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
            lines.move_to(RIGHT * 1.6 + DOWN * 0.3)
            self.play(Write(l1), run_time=1.4)
            self.play(Write(l2), run_time=1.4)
            self.play(Write(l3), run_time=1.6)
            self.play(sq.animate.scale(1.35), run_time=1.0)
            self.play(sq.animate.scale(1 / 1.35), run_time=0.8)

        # --- Roofline ------------------------------------------------------
        ax, ax_labels, (slope, flat) = roofline_axes(width=8.4, height=5.0)
        VGroup(ax, ax_labels, slope, flat).shift(DOWN * 0.2 + RIGHT * 0.3)
        with self.voiceover(
            "A nice way to picture all of this is with what's called a roofline plot. On "
            "the horizontal axis, arithmetic intensity. On the vertical axis, the actual "
            "throughput you achieve."
        ) as vo:
            self.clear_all(run_time=0.7)
            title = T("The roofline model", size=40).to_edge(UP, buff=0.25)
            self.play(Write(title), Create(ax), run_time=1.5)
            self.play(FadeIn(ax_labels[0]), Write(ax_labels[2]), run_time=1.4)
            self.play(FadeIn(ax_labels[1]), Write(ax_labels[3]), run_time=1.4)

        with self.voiceover(
            "At low intensity you're limited by memory bandwidth. Your speed is just "
            "bandwidth times intensity: this slanted line. At high intensity you hit the "
            "ceiling of how fast the chip can compute. The corner where they meet, around "
            "three hundred operations per byte for the H100, is called the ridge point."
        ) as vo:
            bw_l = T("bandwidth × intensity", size=24, color=C_BLUE)
            bw_l.next_to(slope.get_center(), UL, buff=0.1).rotate(
                np.arctan2(*(slope.get_end() - slope.get_start())[1::-1]), about_point=None)
            bw_l.shift(UP * 0.15 + RIGHT * 0.1)
            self.play(Create(slope), run_time=1.6)
            self.play(FadeIn(bw_l), run_time=0.8)
            self.wait(1.2)
            peak_l = T("peak compute ≈ 1,000 TFLOP/s", size=24, color=C_YELLOW)
            peak_l.next_to(flat, UP, buff=0.15)
            self.play(Create(flat), run_time=1.4)
            self.play(FadeIn(peak_l), run_time=0.8)
            self.wait(0.8)
            rp = ax.c2p(ax.ridge, ax.perf(ax.ridge))
            ridge = Dot(rp, radius=0.1, color=C_WHITE)
            dash = DashedLine(rp, ax.c2p(ax.ridge, 0), color=C_GREY)
            r_l = T("ridge ≈ 300", size=24).next_to(ax.c2p(ax.ridge, 0), UP, buff=0.15).shift(
                RIGHT * 0.75)
            self.play(GrowFromCenter(ridge), Create(dash), FadeIn(r_l), run_time=1.2)

        with self.voiceover(
            "Everything to the left is memory-bound. Everything to the right is "
            "compute-bound. Keep this picture in mind, because the story of LLM inference "
            "is really the story of where on this plot each part of the computation lands."
        ) as vo:
            left = Rectangle(width=ax.c2p(ax.ridge, 0)[0] - ax.c2p(0, 0)[0],
                             height=ax.y_length).set_stroke(width=0).set_fill(C_BLUE, 0.12)
            left.move_to(ax.c2p(0, 0), aligned_edge=DL)
            right = Rectangle(width=ax.c2p(4, 0)[0] - ax.c2p(ax.ridge, 0)[0],
                              height=ax.y_length).set_stroke(width=0).set_fill(C_YELLOW, 0.1)
            right.move_to(ax.c2p(ax.ridge, 0), aligned_edge=DL)
            ml = T("memory-bound", size=30, color=C_BLUE).move_to(ax.c2p(1.25, 2.9))
            cl = T("compute-bound", size=30, color=C_YELLOW).move_to(ax.c2p(3.25, 2.3))
            self.play(FadeIn(left), Write(ml), run_time=1.4)
            self.wait(0.6)
            self.play(FadeIn(right), Write(cl), run_time=1.4)
            q = T("?", size=60, color=C_WHITE).move_to(ax.c2p(2.0, 1.4))
            self.play(FadeIn(q, scale=0.5), run_time=0.8)
        self.clear_all()
