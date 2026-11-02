import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403

C_Q = C_YELLOW
C_K = C_GREEN
C_V = C_BLUE


def col_vec(color, n=5, size=0.3, seed=0):
    rng = np.random.default_rng(seed)
    return cell_grid(n, 1, size, color, rng.uniform(0.2, 0.95, (n, 1)), stroke=0.8)


class KVCache(VoiceScene):
    def construct(self):
        self.chapter_card(7, "The KV cache")
        rng = np.random.default_rng(41)
        words = ["The", "GPU", "is", "a", "massively"]
        n = len(words)

        # --- Attention refresher: q . k -> weights -> sum of v ---------------
        toks = VGroup(*[T(w, size=34) for w in words]).arrange(RIGHT, buff=1.0)
        toks.move_to(UP * 2.7 + LEFT * 1.2)
        keys = VGroup(*[col_vec(C_K, seed=i) for i in range(n)])
        vals = VGroup(*[col_vec(C_V, seed=10 + i) for i in range(n)])
        for k, v, t in zip(keys, vals, toks):
            k.next_to(t, DOWN, buff=0.4).shift(LEFT * 0.17)
            v.next_to(k, RIGHT, buff=0.06)
        kl = M("K", 36, C_K).next_to(keys[0], LEFT, buff=0.35)
        vl = M("V", 36, C_V).next_to(kl, DOWN, buff=0.15)
        q = col_vec(C_Q, seed=99).next_to(vals[-1], RIGHT, buff=0.9)
        ql = M(r"\vec{q}", 36, C_Q).next_to(q, UP, buff=0.15)
        with self.voiceover(
            "Remember that in attention, each token produces a query, a key, and a value. "
            "The new token's query is compared against the keys of every previous token, "
            "and those comparisons decide how to weight their values."
        ) as vo:
            self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.1) for t in toks],
                                  lag_ratio=0.15), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(VGroup(k, v)) for k, v in zip(keys, vals)],
                                  lag_ratio=0.15), FadeIn(kl), FadeIn(vl), run_time=1.4)
            self.play(FadeIn(q, shift=LEFT * 0.2), FadeIn(ql), run_time=0.8)
            # dot products -> weights
            weights = rng.dirichlet(np.ones(n) * 0.7)
            wrow = VGroup()
            for i, k in enumerate(keys):
                line = Line(q.get_left(), k.get_right(), color=C_Q, stroke_width=1.5,
                            stroke_opacity=0.6)
                wv = DecimalNumber(weights[i], num_decimal_places=2, font_size=30,
                                   color=C_WHITE)
                wv.next_to(VGroup(k, vals[i]), DOWN, buff=0.3)
                wrow.add(VGroup(line, wv))
            self.play(LaggedStart(*[Create(w[0]) for w in wrow], lag_ratio=0.15), run_time=1.4)
            self.play(LaggedStart(*[FadeIn(w[1], shift=DOWN * 0.1) for w in wrow],
                                  lag_ratio=0.1), *[FadeOut(w[0]) for w in wrow], run_time=1.2)
            # weighted sum of values
            out = col_vec(C_WHITE, seed=5).next_to(wrow, DOWN, buff=1.0).match_x(keys)
            out_l = T("output", size=22, color=C_GREY).next_to(out, DOWN, buff=0.15)
            copies = [vals[i].copy() for i in range(n)]
            self.play(*[c.animate.move_to(out).set_opacity(0.0 + 0.3 * weights[i])
                        for i, c in enumerate(copies)], run_time=1.2)
            self.drop(*copies)
            self.play(FadeIn(out), FadeIn(out_l), run_time=0.6)

        # --- Cache them -----------------------------------------------------
        with self.voiceover(
            "During decode, the keys and values of earlier tokens never change. So rather "
            "than recomputing them every step, we compute them once and store them. This is "
            "called the K V cache."
        ) as vo:
            self.play(FadeOut(VGroup(*[w[1] for w in wrow], out, out_l)), run_time=0.6)
            cache_box = SurroundingRectangle(VGroup(keys, vals, kl, vl), color=C_K,
                                             buff=0.2, corner_radius=0.1)
            cache_l = T("KV cache", size=30, color=C_K).next_to(cache_box, DOWN, buff=0.15)
            self.play(Create(cache_box), Write(cache_l), run_time=1.2)
            self.wait(0.8)
            # append the new token's k and v
            new_t = T("parallel", size=34, color=C_Q).next_to(toks, RIGHT, buff=1.0)
            nk = col_vec(C_K, seed=77)
            nv = col_vec(C_V, seed=78)
            nk.next_to(new_t, DOWN, buff=0.4).shift(LEFT * 0.17)
            nv.next_to(nk, RIGHT, buff=0.06)
            self.play(FadeOut(VGroup(q, ql)), FadeIn(new_t, shift=LEFT * 0.2), run_time=0.8)
            self.play(FadeIn(nk, shift=DOWN * 0.2), FadeIn(nv, shift=DOWN * 0.2), run_time=0.8)
            new_box = SurroundingRectangle(VGroup(keys, vals, kl, vl, nk, nv), color=C_K,
                                           buff=0.2, corner_radius=0.1)
            self.play(Transform(cache_box, new_box), cache_l.animate.next_to(new_box, DOWN, 0.15),
                      run_time=0.8)
            grow = T("grows by one entry per token", size=24, color=C_GREY)
            grow.next_to(cache_l, DOWN, buff=0.15)
            self.play(FadeIn(grow), run_time=0.6)

        # --- How big is it? ------------------------------------------------
        with self.voiceover(
            "How big is it? For our 8 billion parameter model, each token stores a key and "
            "a value, in each of 32 layers, for 8 key-value heads of dimension 128, at two "
            "bytes each. That comes out to about 128 kilobytes per token."
        ) as vo:
            self.clear_all(run_time=0.6)
            parts = [("2", "K and V", C_K), ("32", "layers", C_WHITE),
                     ("8", "KV heads", C_WHITE), ("128", "head dim", C_WHITE),
                     ("2", "bytes", C_BLUE)]
            terms = VGroup()
            for i, (num, lab, col) in enumerate(parts):
                tn = M(num, 64, col)
                tl = T(lab, size=22, color=C_GREY).next_to(tn, DOWN, buff=0.25)
                terms.add(VGroup(tn, tl))
                if i < len(parts) - 1:
                    terms.add(M(r"\times", 52))
            terms.arrange(RIGHT, buff=0.35, aligned_edge=UP).shift(UP * 0.8)
            for t in terms:
                if isinstance(t, MathTex):
                    t.match_y(terms[0][0])
            per = (vo.duration - 3.0) / 5
            for t in terms:
                self.play(FadeIn(t, shift=UP * 0.15), run_time=per * 0.5)
                if not isinstance(t, MathTex):
                    self.wait(per * 0.3)
            res = M(r"= 131{,}072 \text{ bytes} \approx 128\ \text{KB per token}", 52, C_K)
            res.next_to(terms, DOWN, buff=0.8)
            self.play(Write(res), run_time=1.6)

        with self.voiceover(
            "That doesn't sound like much, until you multiply it out. A single "
            "conversation with eight thousand tokens of context needs about a gigabyte. "
            "A batch of sixty four such conversations needs sixty four gigabytes, four "
            "times as much as the model weights themselves!"
        ) as vo:
            self.play(FadeOut(terms), res.animate.scale(0.6).to_edge(UP, buff=0.4),
                      run_time=0.8)
            one = M(r"128\ \text{KB} \times 8{,}192 \text{ tokens} \approx 1\ \text{GB}", 44)
            one.shift(UP * 1.4)
            self.play(Write(one), run_time=1.8)
            many = M(r"1\ \text{GB} \times 64 \text{ conversations} = 64\ \text{GB}", 44, C_K)
            many.next_to(one, DOWN, buff=0.4)
            self.wait(0.6)
            self.play(Write(many), run_time=1.8)
            bar = Rectangle(width=11, height=0.7).set_stroke(C_BLUE, 2).set_fill(C_BLUE, 0.08)
            bar.shift(DOWN * 1.8)
            u = 11 / 80
            wseg = Rectangle(width=16 * u, height=0.7).set_stroke(width=0).set_fill(
                COL_WEIGHT, 0.85).align_to(bar, LEFT).match_y(bar)
            kseg = Rectangle(width=64 * u, height=0.7).set_stroke(width=0).set_fill(
                C_K, 0.75).next_to(wseg, RIGHT, buff=0)
            bl = T("80 GB HBM", size=24, color=C_BLUE).next_to(bar, UP, 0.12).align_to(bar, RIGHT)
            wl = T("weights 16", size=20, color=BLACK).move_to(wseg)
            kl2 = T("KV cache 64 GB", size=24, color=BLACK).move_to(kseg)
            self.play(Create(bar), FadeIn(bl), GrowFromEdge(wseg, LEFT), FadeIn(wl),
                      run_time=1.0)
            self.play(GrowFromEdge(kseg, LEFT), FadeIn(kl2), run_time=1.6)
            full = T("full!", size=36, color=C_RED).next_to(bar, DOWN, buff=0.3)
            self.play(FadeIn(full, scale=1.4), run_time=0.6)
            mem_view = VGroup(bar, wseg, kseg, bl, wl, kl2, full)

        with self.voiceover(
            "And at every decode step, that entire cache has to be read from memory too. "
            "So the K V cache limits how big your batch can be, and it adds more memory "
            "traffic: the exact resource we're already short on."
        ) as vo:
            self.play(FadeOut(VGroup(one, many, res, full)),
                      VGroup(bar, wseg, kseg, bl, wl, kl2).animate.move_to(DOWN * 2.4),
                      run_time=0.8)
            sms = RoundedRectangle(width=6, height=1.2, corner_radius=0.1)
            sms.set_stroke(C_YELLOW, 2).set_fill(C_YELLOW, 0.08).move_to(UP * 1.6)
            sl = T("SMs", size=28, color=C_YELLOW).move_to(sms)
            self.play(FadeIn(sms), FadeIn(sl), run_time=0.6)
            for _ in range(2):
                w_d = VGroup(*[Square(0.14).set_stroke(width=0).set_fill(COL_WEIGHT, 0.9)
                               for _ in range(10)])
                k_d = VGroup(*[Square(0.14).set_stroke(width=0).set_fill(C_K, 0.9)
                               for _ in range(30)])
                for i, d in enumerate(w_d):
                    d.move_to(wseg.get_center() + RIGHT * (i - 5) * 0.15)
                for i, d in enumerate(k_d):
                    d.move_to(kseg.get_center() + RIGHT * (i - 15) * 0.22)
                self.play(LaggedStart(*[d.animate.move_to(sms.get_center()
                                                          + RIGHT * rng.uniform(-2.5, 2.5))
                                        .set_opacity(0) for d in [*w_d, *k_d]],
                                      lag_ratio=0.02), run_time=1.8)
                self.drop(w_d, k_d)
            lim = VGroup(T("limits batch size", size=28, color=C_K),
                         T("adds memory traffic", size=28, color=C_BLUE)).arrange(
                RIGHT, buff=1.2).move_to(UP * 0.0)
            self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in lim], lag_ratio=0.5),
                      run_time=1.4)

        # --- PagedAttention -------------------------------------------------
        with self.voiceover(
            "Early serving systems also wasted a lot of this memory, reserving one big "
            "contiguous chunk for each request's maximum possible length. v L L M's Paged "
            "Attention fixed this with an idea borrowed from operating systems: split the "
            "cache into small, fixed size pages that can live anywhere in memory, and keep a "
            "table of where each sequence's pages are. Almost nothing is wasted, so many more "
            "requests fit in a batch."
        ) as vo:
            self.clear_all(run_time=0.6)
            cols_n, rows_n, cs = 16, 4, 0.5
            # contiguous: each request reserves 8 blocks, uses a few
            left_t = T("Contiguous reservation", size=30).move_to(UP * 3.0 + LEFT * 3.5)
            mem1 = cell_grid(rows_n, cols_n // 2, cs, C_GREY_D, np.zeros((rows_n, 8)),
                             stroke=1, min_opacity=0.0, stroke_color=C_GREY)
            mem1.next_to(left_t, DOWN, buff=0.4)
            used = [3, 6, 2, 5]
            req_cols = [C_PINK, C_GOLD, C_TEAL, C_PURPLE]
            self.play(Write(left_t), FadeIn(mem1), run_time=1.0)
            waste = VGroup()
            for r in range(rows_n):
                anims = []
                for c in range(8):
                    if c < used[r]:
                        anims.append(mem1.cells[r][c].animate.set_fill(req_cols[r], 0.85))
                    else:
                        h = mem1.cells[r][c]
                        anims.append(h.animate.set_fill(req_cols[r], 0.15))
                        x = VGroup(Line(h.get_corner(UL), h.get_corner(DR)),
                                   Line(h.get_corner(DL), h.get_corner(UR))).set_stroke(
                            C_RED, 1.5, opacity=0.6)
                        waste.add(x)
                self.play(*anims, run_time=0.5)
            wl = T("reserved but unused", size=24, color=C_RED).next_to(mem1, DOWN, 0.25)
            self.play(Create(waste), FadeIn(wl), run_time=1.2)
            self.wait(2.0)
            # paged
            right_t = T("Paged (vLLM)", size=30).move_to(UP * 3.0 + RIGHT * 3.5)
            mem2 = cell_grid(rows_n, 8, cs, C_GREY_D, np.zeros((rows_n, 8)), stroke=1,
                             min_opacity=0.0, stroke_color=C_GREY)
            mem2.next_to(right_t, DOWN, buff=0.4)
            self.play(Write(right_t), FadeIn(mem2), run_time=1.0)
            r3 = np.random.default_rng(8)
            free = [(r, c) for r in range(rows_n) for c in range(8)]
            r3.shuffle(free)
            k = 0
            pages = {}
            anims = []
            for ri, u in enumerate(used):
                pages[ri] = []
                for _ in range(u):
                    r, c = free[k]
                    k += 1
                    pages[ri].append((r, c))
                    anims.append(mem2.cells[r][c].animate.set_fill(req_cols[ri], 0.85))
            self.play(LaggedStart(*anims, lag_ratio=0.08), run_time=2.4)
            # page table
            table = VGroup()
            for ri in range(len(used)):
                lab = T(f"seq {ri + 1}:", size=20, color=req_cols[ri])
                ent = T("  ".join(f"{r * 8 + c}" for r, c in pages[ri][:5]) +
                        ("  …" if len(pages[ri]) > 5 else ""), size=18, color=C_GREY)
                table.add(VGroup(lab, ent).arrange(RIGHT, buff=0.2))
            table.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            table.next_to(mem2, DOWN, buff=0.3)
            tt = T("page table", size=22, color=C_WHITE).next_to(table, LEFT, buff=0.3)
            self.play(FadeIn(table), FadeIn(tt), run_time=1.0)
            self.wait(1.5)
            # more requests fit
            more = []
            extra_cols = [C_RED, C_GREEN, C_ORANGE, C_BLUE]
            for j in range(k, len(free)):
                r, c = free[j]
                more.append(mem2.cells[r][c].animate.set_fill(extra_cols[j % 4], 0.85))
            self.play(LaggedStart(*more, lag_ratio=0.05), run_time=min(2.0, self.remaining(vo)))
        self.clear_all()
