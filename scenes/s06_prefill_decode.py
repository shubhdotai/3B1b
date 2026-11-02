import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403


class PrefillDecode(VoiceScene):
    def construct(self):
        self.chapter_card(5, "Prefill and decode")
        rng = np.random.default_rng(21)

        with self.voiceover(
            "Generating a response actually happens in two very different phases."
        ) as vo:
            pre = T("Prefill", size=56, color=C_TEAL)
            dec = T("Decode", size=56, color=C_PINK)
            VGroup(pre, dec).arrange(RIGHT, buff=3.0)
            pre_s = T("read the prompt", size=28, color=C_GREY).next_to(pre, DOWN, 0.3)
            dec_s = T("write the answer", size=28, color=C_GREY).next_to(dec, DOWN, 0.3)
            self.play(Write(pre), FadeIn(pre_s), run_time=1.2)
            self.play(Write(dec), FadeIn(dec_s), run_time=1.2)
        self.play(FadeOut(VGroup(dec, dec_s, pre_s)),
                  pre.animate.scale(0.7).to_corner(UL, buff=0.35), run_time=0.8)

        # --- Prefill: W x X(many tokens) --------------------------------------
        W = cell_grid(8, 8, 0.3, COL_WEIGHT, rng.uniform(0.1, 0.9, (8, 8)), stroke=0.8)
        X = cell_grid(8, 12, 0.3, COL_TOKEN, rng.uniform(0.1, 0.9, (8, 12)), stroke=0.8)
        Y = cell_grid(8, 12, 0.3, C_WHITE, np.zeros((8, 12)), stroke=0.8, min_opacity=0.03)
        eq = VGroup(W, M(r"\times", 36), X, M("=", 36), Y).arrange(RIGHT, buff=0.22)
        eq.move_to(LEFT * 0.0 + DOWN * 0.2)
        with self.voiceover(
            "First comes prefill: reading your prompt, say, a thousand tokens. Since "
            "they're all known up front, they can be processed in parallel. Each weight "
            "matrix multiplies a big matrix holding all thousand token vectors at once."
        ) as vo:
            prompt = VGroup(*[Rectangle(width=0.3, height=0.3).set_stroke(COL_TOKEN, 1)
                              .set_fill(COL_TOKEN, 0.5) for _ in range(30)])
            prompt.arrange(RIGHT, buff=0.05).to_edge(UP, buff=1.3)
            pl = T("prompt: about 1,000 tokens", size=26, color=COL_TOKEN).next_to(prompt, UP, 0.15)
            self.play(LaggedStart(*[FadeIn(p) for p in prompt], lag_ratio=0.03),
                      FadeIn(pl), run_time=1.6)
            self.wait(1.0)
            self.play(FadeIn(W), FadeIn(eq[1]), run_time=0.8)
            self.play(ReplacementTransform(prompt, X), run_time=1.4)
            wl = T("weights", size=24, color=COL_WEIGHT).next_to(W, DOWN, buff=0.2)
            xl = T("all prompt tokens", size=24, color=COL_TOKEN).next_to(X, DOWN, buff=0.2)
            self.play(FadeIn(wl), FadeIn(xl), FadeIn(eq[3]), FadeIn(Y), run_time=0.8)
            vals = rng.uniform(0.3, 1.0, (8, 12))
            self.play(LaggedStart(*[Y.cells[r][c].animate.set_fill(C_WHITE, vals[r, c] * 0.8)
                                    for c in range(12) for r in range(8)], lag_ratio=0.003),
                      run_time=1.2)

        ax, roof = small_roofline()
        with self.voiceover(
            "That means every weight we load from memory gets reused a thousand times. "
            "The arithmetic intensity is high, and prefill lands comfortably on the "
            "compute-bound side of the roofline. The GPU is doing what it was built for."
        ) as vo:
            mat = VGroup(W, eq[1:], wl, xl, pl)
            self.play(mat.animate.scale(0.62).to_edge(LEFT, buff=0.4).shift(DOWN * 0.2),
                      run_time=1.0)
            reuse = T("each weight used 1,000 times", size=26, color=COL_WEIGHT)
            reuse.next_to(mat, DOWN, buff=0.4)
            self.play(Write(reuse), run_time=1.0)
            self.play(FadeIn(roof), run_time=1.2)
            pp = roof_point(ax, 3.0, C_TEAL, "prefill")
            self.play(FadeIn(pp, scale=0.5), run_time=0.8)
            self.play(Flash(pp[0], color=C_TEAL), run_time=0.8)

        # --- Decode -----------------------------------------------------------
        with self.voiceover(
            "Then comes decode, generating the answer. And here's the problem. Each new "
            "token depends on the one before it, so they have to be produced one at a "
            "time. Each step multiplies the weight matrices by just a single vector."
        ) as vo:
            dec.scale(0.7).move_to(pre)
            self.play(FadeOut(VGroup(mat, reuse)), FadeOut(pre), FadeIn(dec), run_time=0.8)
            W2 = cell_grid(8, 8, 0.3, COL_WEIGHT, rng.uniform(0.1, 0.9, (8, 8)), stroke=0.8)
            x1 = cell_grid(8, 1, 0.3, COL_TOKEN, rng.uniform(0.1, 0.9, (8, 1)), stroke=0.8)
            y1 = cell_grid(8, 1, 0.3, C_WHITE, np.zeros((8, 1)), stroke=0.8, min_opacity=0.03)
            eq2 = VGroup(W2, M(r"\times", 36), x1, M("=", 36), y1).arrange(RIGHT, buff=0.22)
            eq2.move_to(LEFT * 3.6 + DOWN * 0.6)
            out_words = ["massively", "parallel", "processor", "..."]
            outs = VGroup(*[T(w, size=26, color=COL_TOKEN) for w in out_words])
            outs.arrange(RIGHT, buff=0.3).next_to(eq2, UP, buff=0.9)
            self.play(FadeIn(eq2), run_time=0.8)
            per = (self.remaining(vo) - 0.3) / len(out_words)
            for i, w in enumerate(outs):
                self.play(*[c.animate.set_fill(C_WHITE, rng.uniform(0.3, 0.9)) for c in y1],
                          run_time=per * 0.45)
                self.play(TransformFromCopy(y1, w), run_time=per * 0.35)
                if i < len(outs) - 1:
                    self.play(*[c.animate.set_fill(COL_TOKEN, rng.uniform(0.1, 0.9))
                                for c in x1],
                              *[c.animate.set_fill(C_WHITE, 0.03) for c in y1],
                              run_time=per * 0.2)

        with self.voiceover(
            "To do that, the GPU has to stream every one of those 16 gigabytes of weights "
            "out of H B M and through the S M's. And for each weight, a pair of bytes, it "
            "does just two operations: one multiply, one add. That's an arithmetic "
            "intensity of about one. Way, way down at the left of the roofline."
        ) as vo:
            self.play(FadeOut(VGroup(eq2, outs)), run_time=0.6)
            hbm = RoundedRectangle(width=4.6, height=1.6, corner_radius=0.1)
            hbm.set_stroke(C_BLUE, 2).set_fill(C_BLUE, 0.15).move_to(LEFT * 3.4 + DOWN * 2.3)
            hbm_l = T("HBM", size=26, color=C_BLUE).next_to(hbm, LEFT, buff=0.15)
            wts = VGroup(*[Square(0.16).set_stroke(width=0).set_fill(COL_WEIGHT, 0.85)
                           for _ in range(6 * 24)])
            wts.arrange_in_grid(rows=6, cols=24, buff=0.03).move_to(hbm)
            wts_l = T("16 GB of weights", size=22, color=COL_WEIGHT).next_to(hbm, DOWN, 0.1)
            sms = RoundedRectangle(width=4.6, height=1.3, corner_radius=0.1)
            sms.set_stroke(C_YELLOW, 2).set_fill(C_YELLOW, 0.08).move_to(LEFT * 3.4 + UP * 1.3)
            cores = VGroup(*[Square(0.13).set_stroke(C_YELLOW, 0.8).set_fill(C_YELLOW, 0.15)
                             for _ in range(4 * 25)])
            cores.arrange_in_grid(rows=4, cols=25, buff=0.04).move_to(sms)
            sms_l = T("SMs", size=26, color=C_YELLOW).next_to(sms, LEFT, buff=0.15)
            pipe = Arrow(hbm.get_top(), sms.get_bottom(), buff=0.1, color=C_BLUE,
                         stroke_width=8, max_tip_length_to_length_ratio=0.15)
            bw = T("3.35 TB/s", size=22, color=C_BLUE).next_to(pipe, RIGHT, buff=0.15)
            self.play(FadeIn(VGroup(hbm, hbm_l, wts, wts_l, sms, cores, sms_l)),
                      GrowArrow(pipe), FadeIn(bw), run_time=1.2)
            # stream the weights up, row by row
            rows = [wts[i * 24:(i + 1) * 24] for i in range(6)]
            for r in rows:
                cp = r.copy()
                self.play(cp.animate.move_to(sms).set_opacity(0.0), run_time=0.55,
                          rate_func=rush_into)
                self.play(cores.animate.set_fill(C_YELLOW, 0.9), run_time=0.05)
                self.play(cores.animate.set_fill(C_YELLOW, 0.15), run_time=0.15)
                self.drop(cp)
            ops = M(r"2 \text{ bytes} \;\rightarrow\; 2 \text{ FLOPs}", 34)
            ops.next_to(sms, UP, buff=0.3)
            self.play(Write(ops), run_time=1.0)
            ai = M(r"\text{intensity} \approx 1", 34, C_PINK).next_to(ops, RIGHT, buff=0.5)
            self.play(Write(ai), run_time=0.8)
            dp = roof_point(ax, 0.0, C_PINK, "decode", direction=RIGHT)
            self.play(FadeIn(dp, scale=0.5), run_time=0.6)
            self.play(Flash(dp[0], color=C_PINK), run_time=0.8)

        # --- The numbers ---------------------------------------------------
        with self.voiceover(
            "Let's put numbers on it. Reading 16 gigabytes at 3.35 terabytes per second "
            "takes about five milliseconds. The math itself, around 16 billion operations, "
            "would take the tensor cores about sixteen microseconds. So during decode, the "
            "compute units are idle more than ninety nine percent of the time."
        ) as vo:
            self.clear_all(run_time=0.6)
            title = T("One decode step, one token", size=40).to_edge(UP, buff=0.5)
            m1 = M(r"\text{memory:}\quad \frac{16\ \text{GB}}{3.35\ \text{TB/s}} "
                   r"\approx 4.8\ \text{ms}", 44, C_BLUE)
            m2 = M(r"\text{compute:}\quad \frac{16\ \text{GFLOP}}{1{,}000\ \text{TFLOP/s}} "
                   r"\approx 0.016\ \text{ms}", 44, C_YELLOW)
            VGroup(m1, m2).arrange(DOWN, buff=0.5, aligned_edge=LEFT).shift(UP * 0.7)
            self.play(Write(title), run_time=0.8)
            self.play(Write(m1), run_time=2.0)
            self.wait(1.0)
            self.play(Write(m2), run_time=2.2)
            # timeline bars
            full = 11.0
            tl = Line(LEFT * full / 2, RIGHT * full / 2, color=C_GREY).shift(DOWN * 2.2)
            mem_bar = Rectangle(width=full, height=0.45).set_stroke(width=0).set_fill(
                C_BLUE, 0.8).move_to(tl).shift(UP * 0.35)
            cmp_bar = Rectangle(width=full * 0.016 / 4.8, height=0.45).set_stroke(
                C_YELLOW, 2).set_fill(C_YELLOW, 1).align_to(mem_bar, LEFT).shift(DOWN * 0.95)
            cmp_bar.match_y(tl).shift(DOWN * 0.35)
            ml = T("loading weights", size=22, color=BLACK).move_to(mem_bar)
            cl = T("math", size=22, color=C_YELLOW).next_to(cmp_bar, RIGHT, buff=0.15)
            self.play(Create(tl), GrowFromEdge(mem_bar, LEFT), FadeIn(ml), run_time=1.6)
            self.play(FadeIn(cmp_bar), FadeIn(cl), run_time=0.8)
            idle = T("tensor cores idle  > 99% of the time", size=32, color=C_RED)
            idle.to_edge(DOWN, buff=0.3)
            self.play(Write(idle), run_time=1.2)

        with self.voiceover(
            "This sets a hard speed limit. No matter how clever the code, one user on this "
            "setup can never get more than about two hundred tokens per second. The speed "
            "of text generation is fundamentally the speed of memory."
        ) as vo:
            self.clear_all(run_time=0.6)
            lim = M(r"\frac{1}{4.8\ \text{ms}} \approx 210\ \text{tokens/s}", 64)
            lim.shift(UP * 0.6)
            sub = T("maximum for a single user", size=30, color=C_GREY).next_to(lim, DOWN, 0.4)
            self.play(Write(lim), run_time=1.8)
            self.play(FadeIn(sub), run_time=0.6)
            self.wait(1.4)
            slogan = T("speed of generation  =  speed of memory", size=40, color=C_BLUE)
            slogan.to_edge(DOWN, buff=1.0)
            self.play(Write(slogan), run_time=1.8)
        self.clear_all()
