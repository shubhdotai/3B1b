import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403


def attention_scores(n, seed=0):
    rng = np.random.default_rng(seed)
    v = rng.uniform(0.1, 1.0, (n, n))
    return v


class FlashAttention(VoiceScene):
    def construct(self):
        self.chapter_card(8, "FlashAttention")
        rng = np.random.default_rng(51)

        # Two regions: on-chip SRAM (top) and HBM (bottom)
        chip_zone = RoundedRectangle(width=13, height=3.3, corner_radius=0.15)
        chip_zone.set_stroke(C_TEAL, 2).set_fill(C_TEAL, 0.05).shift(UP * 1.85)
        chip_l = T("on chip: shared memory (fast, tiny)", size=24, color=C_TEAL)
        chip_l.next_to(chip_zone.get_corner(UL), DR, buff=0.15)
        hbm_zone = RoundedRectangle(width=13, height=2.6, corner_radius=0.15)
        hbm_zone.set_stroke(C_BLUE, 2).set_fill(C_BLUE, 0.08).shift(DOWN * 2.25)
        hbm_l = T("HBM (big, slow)", size=24, color=C_BLUE)
        hbm_l.next_to(hbm_zone.get_corner(UL), DR, buff=0.15)

        with self.voiceover(
            "There's one more place where attention fights against the memory hierarchy, "
            "especially during prefill on long prompts."
        ) as vo:
            self.play(FadeIn(chip_zone), Write(chip_l), run_time=1.2)
            self.play(FadeIn(hbm_zone), Write(hbm_l), run_time=1.2)

        n = 8
        S = cell_grid(n, n, 0.27, C_BLUE, attention_scores(n), stroke=0.6)
        Q = cell_grid(n, 3, 0.27, C_YELLOW, rng.uniform(0.2, 0.9, (n, 3)), stroke=0.6)
        Kt = cell_grid(3, n, 0.27, C_GREEN, rng.uniform(0.2, 0.9, (3, n)), stroke=0.6)
        eq = VGroup(Q, M(r"\times", 30), Kt, M("=", 30), S).arrange(RIGHT, buff=0.2)
        eq.move_to(chip_zone).shift(DOWN * 0.35 + LEFT * 0.3)
        lq = M("Q", 28, C_YELLOW).next_to(Q, UP, 0.1)
        lk = M("K^T", 28, C_GREEN).next_to(Kt, UP, 0.1)
        ls = T("scores  N × N", size=22, color=C_BLUE).next_to(S, UP, 0.1)
        traffic = Integer(0, font_size=34, color=C_BLUE)
        traffic_l = T("HBM trips for the score grid:", size=22, color=C_BLUE)
        tgrp = VGroup(traffic_l, traffic).arrange(RIGHT, buff=0.2)
        tgrp.next_to(hbm_zone.get_corner(UR), DL, buff=0.2)
        with self.voiceover(
            "Computing attention naively means forming the full grid of scores, every "
            "query against every key. For a prompt of N tokens, that's an N by N matrix. "
            "The straightforward approach writes this whole grid out to H B M, reads it "
            "back to apply the softmax, writes it out again, then reads it back once more "
            "to multiply by the values."
        ) as vo:
            self.play(FadeIn(VGroup(Q, Kt, eq[1], eq[3], lq, lk)), run_time=0.8)
            self.play(FadeIn(S), Write(ls), run_time=1.4)
            self.wait(1.6)
            self.play(FadeIn(tgrp), run_time=0.5)
            down_pos = hbm_zone.get_center() + DOWN * 0.15
            up_pos = S.get_center()
            steps = [("write S", down_pos, 1), ("read S", up_pos, 2),
                     ("softmax", None, 2), ("write P", down_pos, 3), ("read P", up_pos, 4)]
            note = None
            for lab, pos, cnt in steps:
                t = T(lab, size=26, color=C_WHITE).move_to(RIGHT * 4.6 + UP * 1.5)
                anims = [FadeIn(t)]
                if note is not None:
                    anims.append(FadeOut(note))
                if pos is not None:
                    anims += [S.animate.move_to(pos), ChangeDecimalToValue(traffic, cnt)]
                    if lab.startswith("write"):
                        pass
                else:
                    vals = rng.uniform(0.1, 1.0, (n, n))
                    vals = vals / vals.max()
                    anims += [S.cells[r][c].animate.set_fill(C_PINK, vals[r, c])
                              for r in range(n) for c in range(n)]
                self.play(*anims, run_time=1.3)
                note = t
            V = cell_grid(n, 3, 0.27, C_PURPLE, rng.uniform(0.2, 0.9, (n, 3)), stroke=0.6)
            O = cell_grid(n, 3, 0.27, C_WHITE, rng.uniform(0.2, 0.9, (n, 3)), stroke=0.6)
            tail = VGroup(M(r"\times", 30), V, M("=", 30), O).arrange(RIGHT, buff=0.2)
            tail.next_to(S, RIGHT, buff=0.2)
            self.play(FadeOut(note), FadeIn(tail), run_time=min(1.0, self.remaining(vo)))

        with self.voiceover(
            "For long contexts this grid is enormous, and all that back and forth traffic "
            "with H B M dominates the run time."
        ) as vo:
            big = M(r"N = 8{,}192 \;\Rightarrow\; N^2 \approx 67 \text{ million scores}", 34,
                    C_BLUE)
            big2 = T("per head, per layer", size=24, color=C_GREY)
            g = VGroup(big, big2).arrange(DOWN, buff=0.15).move_to(hbm_zone).shift(DOWN * 0.3)
            self.play(Write(big), FadeIn(big2), run_time=1.6)
            self.play(Indicate(tgrp, color=C_RED), run_time=1.0)

        # --- Flash: tile it ------------------------------------------------
        with self.voiceover(
            "FlashAttention restructures the computation using the same tiling idea from "
            "before. Load a block of queries into shared memory. Then stream through the "
            "keys and values one block at a time, computing that small patch of scores, and "
            "folding it into the output right away."
        ) as vo:
            self.play(FadeOut(VGroup(Q, Kt, eq[1], eq[3], lq, lk, S, ls, tail, g, tgrp)),
                      run_time=0.8)
            # Inputs live in HBM
            Qh = cell_grid(n, 3, 0.22, C_YELLOW, rng.uniform(0.2, 0.9, (n, 3)), stroke=0.6)
            Kh = cell_grid(n, 3, 0.22, C_GREEN, rng.uniform(0.2, 0.9, (n, 3)), stroke=0.6)
            Vh = cell_grid(n, 3, 0.22, C_PURPLE, rng.uniform(0.2, 0.9, (n, 3)), stroke=0.6)
            Oh = cell_grid(n, 3, 0.22, C_WHITE, np.zeros((n, 3)), stroke=0.6, min_opacity=0.03)
            hb = VGroup(Qh, Kh, Vh, Oh).arrange(RIGHT, buff=0.9).move_to(hbm_zone).shift(
                DOWN * 0.15 + RIGHT * 0.5)
            hl = VGroup(*[M(s, 26, c).next_to(m, LEFT, 0.12) for s, c, m in
                          [("Q", C_YELLOW, Qh), ("K", C_GREEN, Kh), ("V", C_PURPLE, Vh),
                           ("O", C_WHITE, Oh)]])
            self.play(FadeIn(hb), FadeIn(hl), run_time=0.8)
            # On chip: score grid as ghost, 4x4 tiles of 2x2
            Sg = cell_grid(n, n, 0.27, C_BLUE, np.zeros((n, n)), stroke=0.6,
                           min_opacity=0.0, stroke_color=C_GREY_D)
            Sg.move_to(chip_zone).shift(DOWN * 0.15)
            sg_l = T("scores: never stored whole", size=22, color=C_GREY).next_to(Sg, LEFT, 0.3)
            self.play(FadeIn(Sg), FadeIn(sg_l), run_time=0.6)
            bs = 2
            qrow_blocks = 2  # animate the first two query blocks in detail
            for qi in range(n // bs):
                qb = VGroup(*[Qh.cells[r][c] for r in range(qi * bs, qi * bs + bs)
                              for c in range(3)])
                qcopy = qb.copy()
                rt = 0.45 if qi < qrow_blocks else 0.18
                self.play(qcopy.animate.next_to(Sg, RIGHT, buff=0.4), run_time=rt)
                for kj in range(n // bs):
                    kb = VGroup(*[Kh.cells[r][c] for r in range(kj * bs, kj * bs + bs)
                                  for c in range(3)])
                    vb = VGroup(*[Vh.cells[r][c] for r in range(kj * bs, kj * bs + bs)
                                  for c in range(3)])
                    kc, vc = kb.copy(), vb.copy()
                    tile = VGroup(*[Sg.cells[r][c] for r in range(qi * bs, qi * bs + bs)
                                    for c in range(kj * bs, kj * bs + bs)])
                    self.play(kc.animate.next_to(Sg, UP, buff=0.05).set_opacity(0.0),
                              vc.animate.next_to(Sg, UP, buff=0.05).set_opacity(0.0),
                              tile.animate.set_fill(C_BLUE, 0.9), run_time=rt)
                    self.drop(kc, vc)
                    self.play(tile.animate.set_fill(C_BLUE, 0.0), run_time=rt * 0.6)
                ob = VGroup(*[Oh.cells[r][c] for r in range(qi * bs, qi * bs + bs)
                              for c in range(3)])
                self.play(qcopy.animate.move_to(ob).set_opacity(0),
                          ob.animate.set_fill(C_WHITE, 0.8), run_time=rt)
                self.drop(qcopy)

        # --- Online softmax ------------------------------------------------
        with self.voiceover(
            "The tricky part is the softmax, which normally needs to see an entire row "
            "before it can normalize. The solution: keep a running maximum and a running "
            "sum for each row. Whenever a new block reveals a larger maximum, you simply "
            "rescale what you've accumulated so far. The final answer is exactly the same, "
            "but the giant N by N matrix never touches H B M at all."
        ) as vo:
            self.clear_all(run_time=0.6)
            title = T("Online softmax", size=40).to_edge(UP, buff=0.4)
            s1 = [1.0, 2.0, 0.5, 1.5]
            s2 = [3.0, 0.2, 2.5, 1.0]

            def row_of(vals, col):
                g = VGroup()
                for v in vals:
                    sq = Square(0.7).set_stroke(col, 2).set_fill(col, 0.15 + 0.2 * v)
                    g.add(VGroup(sq, DecimalNumber(v, num_decimal_places=1, font_size=26)
                                 .move_to(sq)))
                return g.arrange(RIGHT, buff=0.08)

            b1, b2 = row_of(s1, C_BLUE), row_of(s2, C_BLUE)
            row = VGroup(b1, b2).arrange(RIGHT, buff=0.5).shift(UP * 1.6)
            l1 = T("block 1", size=22, color=C_GREY).next_to(b1, UP, 0.15)
            l2 = T("block 2", size=22, color=C_GREY).next_to(b2, UP, 0.15)
            self.play(Write(title), FadeIn(b1), FadeIn(l1), run_time=1.2)
            m_t = M(r"m", 40, C_YELLOW)
            m_v = DecimalNumber(2.0, num_decimal_places=1, font_size=40, color=C_YELLOW)
            l_t = M(r"\ell", 40, C_GREEN)
            l_v = DecimalNumber(2.20, num_decimal_places=2, font_size=40, color=C_GREEN)
            m_row = VGroup(T("running max", size=26, color=C_YELLOW), m_t, M("=", 40), m_v)
            l_row = VGroup(T("running sum", size=26, color=C_GREEN), l_t, M("=", 40), l_v)
            for r in (m_row, l_row):
                r.arrange(RIGHT, buff=0.25)
            stats = VGroup(m_row, l_row).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
            stats.shift(DOWN * 0.3 + LEFT * 2.5)
            sum_f = M(r"\ell = \sum_j e^{\,s_j - m}", 38).next_to(stats, RIGHT, buff=1.2)
            self.play(Indicate(b1[1], color=C_YELLOW), FadeIn(m_row), run_time=1.2)
            self.play(FadeIn(l_row), Write(sum_f), run_time=1.4)
            self.wait(0.6)
            self.play(FadeIn(b2), FadeIn(l2), run_time=0.8)
            self.play(Indicate(b2[0], color=C_YELLOW, scale_factor=1.3), run_time=0.9)
            resc = M(r"\ell \leftarrow \ell \cdot e^{\,m_{\text{old}} - m_{\text{new}}}"
                     r" + \sum_{j \in \text{block 2}} e^{\,s_j - m_{\text{new}}}", 36, C_GREEN)
            resc.next_to(stats, DOWN, buff=0.6).align_to(stats, LEFT)
            self.play(ChangeDecimalToValue(m_v, 3.0), run_time=0.8)
            self.play(Write(resc), run_time=2.0)
            self.play(ChangeDecimalToValue(l_v, 2.61), run_time=1.0)
            same = T("= exactly the full-row softmax sum", size=26, color=C_WHITE)
            same.next_to(resc, DOWN, buff=0.4).align_to(resc, LEFT)
            check = Text("✓", font="DejaVu Sans", font_size=40, color=C_GREEN).next_to(same, RIGHT, buff=0.2)
            self.play(FadeIn(same), FadeIn(check, scale=1.5), run_time=1.0)

        with self.voiceover(
            "Same math, a fraction of the memory traffic, and often several times faster. "
            "It's a beautiful example of a recurring theme: on modern hardware, the "
            "cleverest algorithm is often the one that moves the fewest bytes."
        ) as vo:
            self.clear_all(run_time=0.6)
            ax_l = T("HBM traffic for attention (long prompt)", size=28).to_edge(UP, 0.8)
            nb = Rectangle(width=10, height=0.8).set_stroke(width=0).set_fill(C_BLUE, 0.8)
            fb = Rectangle(width=1.2, height=0.8).set_stroke(width=0).set_fill(C_TEAL, 0.9)
            nl = T("naive", size=28, color=C_BLUE)
            fl = T("FlashAttention", size=28, color=C_TEAL)
            rows = VGroup(VGroup(nl, nb).arrange(RIGHT, buff=0.3),
                          VGroup(fl, fb).arrange(RIGHT, buff=0.3)).arrange(
                DOWN, buff=0.6, aligned_edge=LEFT)
            nb.align_to(fb, LEFT)
            rows.move_to(UP * 0.4)
            self.play(Write(ax_l), FadeIn(nl), FadeIn(fl), run_time=1.0)
            self.play(GrowFromEdge(nb, LEFT), run_time=1.2)
            self.play(GrowFromEdge(fb, LEFT), run_time=0.8)
            moral = T("The cleverest algorithm moves the fewest bytes.", size=36,
                      color=C_YELLOW).to_edge(DOWN, buff=1.0)
            self.play(Write(moral), run_time=2.0)
        self.clear_all()
