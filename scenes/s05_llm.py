import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403


def vec_column(n=8, size=0.28, color=COL_TOKEN, seed=0):
    rng = np.random.default_rng(seed)
    return cell_grid(n, 1, size, color, rng.uniform(0.15, 0.95, (n, 1)))


class LLMRecap(VoiceScene):
    def construct(self):
        self.chapter_card(4, "What an LLM computes")

        words = ["The", "GPU", "is", "a"]
        with self.voiceover(
            "Quick refresher on what a language model actually computes. If you've "
            "seen how transformers work, this will be familiar."
        ) as vo:
            toks = VGroup(*[T(w, size=34) for w in words]).arrange(RIGHT, buff=0.9)
            toks.to_edge(UP, buff=0.9).shift(LEFT * 2.5)
            boxes = VGroup(*[SurroundingRectangle(t, buff=0.1, color=C_GREY,
                                                  corner_radius=0.05) for t in toks])
            self.play(LaggedStart(*[FadeIn(VGroup(b, t), shift=DOWN * 0.2)
                                    for b, t in zip(boxes, toks)], lag_ratio=0.25),
                      run_time=2.0)

        vecs = VGroup(*[vec_column(seed=i) for i in range(4)])
        for v, t in zip(vecs, toks):
            v.next_to(t, DOWN, buff=0.6)
        layers = VGroup()
        with self.voiceover(
            "The text is broken into tokens, and each token is turned into a long vector "
            "of numbers. These vectors flow through a sequence of layers. In each layer, "
            "an attention block lets the vectors exchange information with each other, and "
            "a multilayer perceptron block updates each vector on its own."
        ) as vo:
            arrows = VGroup(*[Arrow(t.get_bottom(), v.get_top(), buff=0.1, color=C_GREY,
                                    stroke_width=2, max_tip_length_to_length_ratio=0.3)
                              for t, v in zip(toks, vecs)])
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2),
                      LaggedStart(*[FadeIn(v, shift=DOWN * 0.2) for v in vecs],
                                  lag_ratio=0.2), run_time=2.0)
            # layer stack on the right
            for i in range(3):
                att = labeled_box("Attention", 2.6, 0.55, color=C_BLUE, size=22)
                mlp = labeled_box("MLP", 2.6, 0.55, color=C_GREEN, size=22)
                layers.add(att, mlp)
            layers.arrange(DOWN, buff=0.12)
            dots = M(r"\vdots", 36).next_to(layers, DOWN, buff=0.1)
            x32 = T("× 32 layers", size=24, color=C_GREY).next_to(layers, RIGHT, buff=0.2)
            stack = VGroup(layers, dots, x32).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.3)
            self.play(LaggedStart(*[FadeIn(l, shift=LEFT * 0.2) for l in layers],
                                  lag_ratio=0.1), FadeIn(dots), FadeIn(x32), run_time=1.6)
            self.wait(1.2)
            # attention: curved arrows between vectors
            self.play(Indicate(layers[0], color=C_BLUE), run_time=0.8)
            links = VGroup()
            for i in range(4):
                for j in range(i):
                    links.add(CurvedArrow(vecs[j].get_bottom() + DOWN * 0.1,
                                          vecs[i].get_bottom() + DOWN * 0.1,
                                          angle=PI / 2.5, color=C_BLUE, stroke_width=2,
                                          tip_length=0.15))
            self.play(LaggedStart(*[Create(l) for l in links], lag_ratio=0.1), run_time=1.6)
            rng = np.random.default_rng(9)
            self.play(*[c.animate.set_fill(COL_TOKEN, rng.uniform(0.15, 0.95))
                        for v in vecs for c in v], run_time=0.8)
            self.play(FadeOut(links), run_time=0.5)
            self.play(Indicate(layers[1], color=C_GREEN), run_time=0.8)
            for v in vecs:
                self.play(Indicate(v, color=C_GREEN, scale_factor=1.1),
                          *[c.animate.set_fill(COL_TOKEN, rng.uniform(0.15, 0.95))
                            for c in v], run_time=0.4)

        with self.voiceover(
            "At the end, the last vector is turned into a probability distribution over "
            "every possible next token. One is sampled, appended to the text, and the "
            "whole process repeats."
        ) as vo:
            cands = [("massively", 0.34), ("graphics", 0.22), ("parallel", 0.17),
                     ("specialized", 0.12), ("chip", 0.08)]
            bars = VGroup()
            for w, p in cands:
                lab = T(w, size=22)
                bar = Rectangle(width=p * 6, height=0.3).set_stroke(width=0).set_fill(
                    C_YELLOW, 0.8)
                pl = T(f"{int(p * 100)}%", size=18, color=C_GREY)
                row = VGroup(lab, bar, pl)
                lab.next_to(bar, LEFT, buff=0.2)
                pl.next_to(bar, RIGHT, buff=0.15)
                bars.add(row)
            for i, b in enumerate(bars):
                b[1].align_to(bars[0][1], LEFT)
                b.shift(DOWN * i * 0.45)
                b[0].next_to(b[1], LEFT, buff=0.2)
                b[2].next_to(b[1], RIGHT, buff=0.15)
            bars.next_to(vecs, DOWN, buff=0.7).match_x(vecs)
            last = vecs[3]
            arr = Arrow(last.get_bottom(), bars.get_top() + RIGHT * 1.0, color=C_YELLOW,
                        buff=0.1)
            self.play(Indicate(last, color=C_YELLOW), GrowArrow(arr), run_time=1.0)
            self.play(LaggedStart(*[GrowFromEdge(b[1], LEFT) for b in bars],
                                  lag_ratio=0.1),
                      LaggedStart(*[FadeIn(VGroup(b[0], b[2])) for b in bars],
                                  lag_ratio=0.1), run_time=1.4)
            pick = SurroundingRectangle(bars[0], color=C_YELLOW, buff=0.06)
            self.play(Create(pick), run_time=0.6)
            new_tok = T("massively", size=34, color=C_YELLOW)
            new_tok.next_to(toks, RIGHT, buff=0.9)
            new_box = SurroundingRectangle(new_tok, buff=0.1, color=C_YELLOW,
                                           corner_radius=0.05)
            self.play(TransformFromCopy(bars[0][0], new_tok), Create(new_box), run_time=1.2)
            loop = CurvedArrow(new_box.get_bottom() + DOWN * 0.1,
                               vecs[3].get_right() + RIGHT * 0.3, angle=-PI / 3,
                               color=C_GREY)
            self.play(Create(loop), run_time=0.8)
            again = T("repeat", size=24, color=C_GREY).next_to(loop, RIGHT, buff=0.1)
            self.play(FadeIn(again), run_time=0.4)

        # --- Everything is weights x vectors -------------------------------
        with self.voiceover(
            "Notice that almost every step here is a matrix multiplication: a big matrix "
            "of learned weights, multiplied by the token vectors. The attention "
            "projections, the MLP layers, the final unembedding. All weights. All matrix "
            "products."
        ) as vo:
            self.clear_all(run_time=0.6)
            names = [r"W_Q", r"W_K", r"W_V", r"W_O", r"W_{\uparrow}", r"W_{\downarrow}",
                     r"W_U"]
            rng = np.random.default_rng(11)
            mats = VGroup()
            for i, nm in enumerate(names):
                g = cell_grid(6, 6, 0.2, COL_WEIGHT, rng.uniform(0.1, 0.9, (6, 6)),
                              stroke=0.6)
                lab = M(nm, 30, COL_WEIGHT).next_to(g, UP, buff=0.12)
                mats.add(VGroup(lab, g))
            mats.arrange(RIGHT, buff=0.45).shift(UP * 1.2)
            grp_l = VGroup(
                Brace(mats[:4], DOWN, color=C_BLUE),
                Brace(mats[4:6], DOWN, color=C_GREEN),
                Brace(mats[6:], DOWN, color=C_GREY),
            )
            gl = VGroup(T("attention", size=22, color=C_BLUE).next_to(grp_l[0], DOWN, 0.1),
                        T("MLP", size=22, color=C_GREEN).next_to(grp_l[1], DOWN, 0.1),
                        T("unembed", size=22, color=C_GREY).next_to(grp_l[2], DOWN, 0.1))
            self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in mats],
                                  lag_ratio=0.15), run_time=2.4)
            self.play(LaggedStart(*[GrowFromCenter(b) for b in grp_l], lag_ratio=0.2),
                      LaggedStart(*[FadeIn(g) for g in gl], lag_ratio=0.2), run_time=1.6)
            W = cell_grid(6, 6, 0.35, COL_WEIGHT, rng.uniform(0.1, 0.9, (6, 6)))
            x = vec_column(6, 0.35, seed=4)
            y = cell_grid(6, 1, 0.35, C_WHITE, rng.uniform(0.1, 0.9, (6, 1)))
            eq = VGroup(W, M(r"\times", 40), x, M("=", 40), y).arrange(RIGHT, buff=0.3)
            eq.to_edge(DOWN, buff=0.5)
            wl = T("weights", size=22, color=COL_WEIGHT).next_to(W, LEFT, buff=0.2)
            xl = T("token vector", size=22, color=COL_TOKEN).next_to(x, DOWN, buff=0.15)
            self.play(FadeIn(eq), FadeIn(wl), FadeIn(xl), run_time=1.4)

        with self.voiceover(
            "And there are a lot of weights. An open model like Llama 3 with 8 billion "
            "parameters, at two bytes each, takes up 16 gigabytes, and frontier models are "
            "far larger. For our running example, let's put that 8 billion parameter model "
            "on one H100."
        ) as vo:
            self.clear_all(run_time=0.6)
            l1 = M(r"8{,}000{,}000{,}000 \ \text{parameters}", 48, COL_WEIGHT)
            l2 = M(r"\times\ 2 \ \text{bytes each (16-bit)}", 44, C_WHITE)
            l3 = M(r"=\ 16\ \text{GB}", 60, C_BLUE)
            col = VGroup(l1, l2, l3).arrange(DOWN, buff=0.4).shift(UP * 1.0)
            self.play(Write(l1), run_time=1.6)
            self.play(Write(l2), run_time=1.2)
            self.play(Write(l3), run_time=1.0)
            self.wait(1.0)
            # memory bar: 80 GB HBM with 16 GB of weights
            bar = Rectangle(width=10, height=0.7).set_stroke(C_BLUE, 2).set_fill(C_BLUE, 0.1)
            bar.to_edge(DOWN, buff=1.2)
            wfill = Rectangle(width=10 * 16 / 80, height=0.7).set_stroke(width=0).set_fill(
                COL_WEIGHT, 0.75).align_to(bar, LEFT).match_y(bar)
            bl = T("H100 memory: 80 GB", size=26, color=C_BLUE).next_to(bar, UP, buff=0.15)
            bl.align_to(bar, RIGHT)
            wl2 = T("weights 16 GB", size=22, color=BLACK).move_to(wfill)
            self.play(Create(bar), FadeIn(bl), run_time=1.0)
            self.play(GrowFromEdge(wfill, LEFT), FadeIn(wl2), run_time=1.2)
            self.play(Indicate(wfill, color=COL_WEIGHT, scale_factor=1.05), run_time=1.0)
        self.clear_all()
