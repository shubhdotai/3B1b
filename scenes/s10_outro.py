import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403


def bit_strip(bits, cell=0.32, color=COL_WEIGHT):
    g = VGroup(*[Square(cell).set_stroke(color, 1.2).set_fill(color, 0.6)
                 for _ in range(bits)]).arrange(RIGHT, buff=0.03)
    return g


def token_chip(word, color, dashed=False, size=26):
    t = T(word, size=size, color=color)
    box = SurroundingRectangle(t, buff=0.12, corner_radius=0.06, color=color)
    if dashed:
        box = DashedVMobject(box, num_dashes=24)
    return VGroup(box, t)


class Outro(VoiceScene):
    def construct(self):
        self.chapter_card(9, "Thinking in bytes")

        with self.voiceover(
            "Once you see the world in terms of bytes moved, a lot of the other tricks in "
            "modern inference start to make sense."
        ) as vo:
            slogan = M(r"\text{time per token} \;\approx\; "
                       r"\frac{\text{bytes moved}}{\text{memory bandwidth}}", 48)
            slogan[0][13:24].set_color(C_BLUE)
            self.play(Write(slogan), run_time=2.2)
            self.wait(self.remaining(vo) - 0.8)
            self.play(slogan.animate.scale(0.6).to_edge(UP, buff=0.3), run_time=0.8)

        # --- Quantization ---------------------------------------------------
        with self.voiceover(
            "Quantization stores each weight with fewer bits: say eight, or even four, "
            "instead of sixteen. Fewer bytes to read per token means faster decoding, "
            "almost in direct proportion."
        ) as vo:
            title = T("Quantization", size=40, color=COL_WEIGHT).next_to(slogan, DOWN, 0.4)
            self.play(Write(title), run_time=0.8)
            rows = VGroup()
            for bits, gb, tps in [(16, 16, 210), (8, 8, 420), (4, 4, 840)]:
                lab = T(f"{bits}-bit", size=28).set_width(1.1)
                strip = bit_strip(bits)
                info = T(f"{gb} GB  →  ≈ {tps} tokens/s", size=26, color=C_BLUE)
                rows.add(VGroup(lab, strip, info))
            for r in rows:
                r[1].next_to(r[0], RIGHT, buff=0.4)
            rows.arrange(DOWN, buff=0.55, aligned_edge=LEFT).shift(DOWN * 0.6 + LEFT * 2.6)
            for r in rows:
                r[1].align_to(rows[0][1], LEFT)
                r[2].move_to(RIGHT * 4.0).match_y(r[1])
            self.play(FadeIn(rows[0][0]), FadeIn(rows[0][1]), run_time=0.8)
            self.play(FadeIn(rows[0][2]), run_time=0.6)
            for i in (1, 2):
                self.play(FadeIn(rows[i][0]),
                          TransformFromCopy(rows[i - 1][1], rows[i][1]), run_time=1.0)
                self.play(FadeIn(rows[i][2], shift=RIGHT * 0.2), run_time=0.6)
            self.play(Indicate(VGroup(*[r[2] for r in rows]), color=C_BLUE), run_time=1.2)

        # --- Speculative decoding ------------------------------------------
        with self.voiceover(
            "Speculative decoding uses a small, fast draft model to guess the next several "
            "tokens. The big model then checks all of those guesses in a single pass. Since "
            "checking several tokens at once is like a tiny prefill, it costs about the same "
            "as generating one. Every guess that turns out right is a token you got nearly "
            "for free."
        ) as vo:
            self.play(FadeOut(VGroup(title, rows)), run_time=0.6)
            title = T("Speculative decoding", size=40, color=C_PINK).next_to(slogan, DOWN, 0.4)
            draft = labeled_box("draft model", 2.4, 0.9, color=C_TEAL, size=24)
            big = labeled_box("big model", 3.4, 1.4, color=C_PINK, size=30)
            draft.move_to(LEFT * 4.6 + UP * 0.4)
            big.move_to(LEFT * 4.6 + DOWN * 1.9)
            self.play(Write(title), FadeIn(draft), FadeIn(big), run_time=1.2)
            words = ["massively", "parallel", "processor", "that"]
            guesses = VGroup(*[token_chip(w, C_TEAL, dashed=True) for w in words])
            guesses.arrange(RIGHT, buff=0.25).move_to(RIGHT * 1.6 + UP * 0.4)
            self.play(LaggedStart(*[FadeIn(g, shift=RIGHT * 0.3) for g in guesses],
                                  lag_ratio=0.25), run_time=1.6)
            fast = T("cheap guesses", size=22, color=C_TEAL).next_to(guesses, UP, 0.2)
            self.play(FadeIn(fast), run_time=0.5)
            # verification in one pass
            beams = VGroup(*[Line(big.get_right(), g.get_bottom(), color=C_PINK,
                                  stroke_width=2, stroke_opacity=0.7) for g in guesses])
            one = T("one pass checks all four", size=24, color=C_PINK)
            one.next_to(guesses, DOWN, buff=1.6)
            self.play(LaggedStart(*[Create(b) for b in beams], lag_ratio=0.0),
                      FadeIn(one), run_time=1.2)
            marks = VGroup()
            for i, g in enumerate(guesses):
                ok = i < 3
                mk = Text("✓" if ok else "✗", font="DejaVu Sans", font_size=36,
                          color=C_GREEN if ok else C_RED).next_to(g, UP, buff=0.2)
                marks.add(mk)
            self.play(FadeOut(fast), FadeOut(beams), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(m, scale=1.5) for m in marks], lag_ratio=0.3),
                      run_time=1.4)
            fix = token_chip("with", C_PINK).move_to(guesses[3]).shift(DOWN * 0.9)
            self.play(guesses[:3].animate.set_color(C_GREEN), guesses[3].animate.set_opacity(0.3),
                      FadeIn(fix, shift=UP * 0.2), run_time=1.0)
            res = T("4 tokens for roughly the cost of 1 big step", size=26, color=C_WHITE)
            res.next_to(one, DOWN, buff=0.3)
            self.play(Write(res), run_time=1.2)

        # --- Multi-GPU ------------------------------------------------------
        with self.voiceover(
            "And for models too large for one chip, the weights are split across many GPUs, "
            "connected by very high bandwidth links, so that each chip only has to stream its "
            "own slice."
        ) as vo:
            self.play(FadeOut(VGroup(title, draft, big, guesses, marks, fix, one, res)),
                      run_time=0.6)
            rng = np.random.default_rng(61)
            W = cell_grid(8, 16, 0.22, COL_WEIGHT, rng.uniform(0.1, 0.9, (8, 16)), stroke=0.6)
            W.move_to(UP * 0.9)
            wl = T("weights of a huge model", size=24, color=COL_WEIGHT).next_to(W, LEFT, 0.3)
            self.play(FadeIn(W), FadeIn(wl), run_time=0.8)
            chips = VGroup()
            for i in range(8):
                box = RoundedRectangle(width=1.2, height=1.0, corner_radius=0.08)
                box.set_stroke(C_YELLOW, 2).set_fill("#111418", 1)
                cores = VGroup(*[Square(0.12).set_stroke(C_YELLOW, 0.6).set_fill(C_YELLOW, 0.3)
                                 for _ in range(24)]).arrange_in_grid(4, 6, buff=0.04)
                cores.move_to(box)
                lab = T(f"GPU {i + 1}", size=18, color=C_GREY).next_to(box, DOWN, 0.1)
                chips.add(VGroup(box, cores, lab))
            chips.arrange(RIGHT, buff=0.35).to_edge(DOWN, buff=0.6)
            links = VGroup(*[Line(chips[i][0].get_right(), chips[i + 1][0].get_left(),
                                  color=C_GREEN, stroke_width=4) for i in range(7)])
            nv = T("high-bandwidth GPU-to-GPU links", size=22, color=C_GREEN)
            nv.next_to(chips, UP, buff=0.15)
            self.play(LaggedStart(*[FadeIn(c) for c in chips], lag_ratio=0.08),
                      Create(links), FadeIn(nv), run_time=1.4)
            slices = [VGroup(*[W.cells[r][c] for r in range(8) for c in (2 * i, 2 * i + 1)])
                      for i in range(8)]
            self.play(*[s.copy().animate.scale(0.35).move_to(chips[i][0])
                        for i, s in enumerate(slices)],
                      run_time=min(2.0, self.remaining(vo) - 0.2))

        # --- Recap ---------------------------------------------------------
        with self.voiceover(
            "So next time you watch an answer stream onto your screen, picture what's "
            "underneath. For every token, billions of weights flow up out of high bandwidth "
            "memory, into thousands of tiny arithmetic units that finish almost instantly, "
            "and then wait for more."
        ) as vo:
            self.clear_all(run_time=0.6)
            chip = gpu_chip(width=6.4, height=4.0)
            chip.shift(DOWN * 0.5)
            self.play(FadeIn(chip), run_time=1.0)
            sentence = "The math was never really the hard part."
            full = T(sentence, size=34).to_edge(UP, buff=0.5)
            out_words, line, k = sentence.split(" "), VGroup(), 0
            for wd in out_words:  # Text submobjects are glyphs (spaces excluded)
                line.add(VGroup(*full[k:k + len(wd)]))
                k += len(wd)
            per = (vo.duration - 1.6) / len(out_words)
            for i, w in enumerate(line):
                flows = []
                dots_all = VGroup()
                for st in chip.hbm:
                    start = st.get_center()
                    end = chip.die.get_center() + (start - chip.die.get_center()) * 0.2
                    d = stream_dots(start, end, n=4, color=COL_WEIGHT, radius=0.05)
                    dots_all.add(*d)
                    flows.append(flow_animation(d, start, end, run_time=per * 0.7, lag=0.15))
                self.play(*flows, run_time=per * 0.7)
                self.drop(dots_all)
                self.play(chip.sms.animate.set_fill(C_YELLOW, 0.9), FadeIn(w, shift=UP * 0.1),
                          run_time=per * 0.1)
                self.play(chip.sms.animate.set_fill(C_YELLOW, 0.2), run_time=per * 0.2)
            self.end_line = full

        with self.voiceover(
            "The math was never really the hard part. The hard part is feeding it."
        ) as vo:
            self.play(FadeOut(chip), self.end_line.animate.move_to(UP * 0.6).scale(1.3),
                      run_time=1.2)
            l2 = T("The hard part is feeding it.", size=42, color=C_BLUE)
            l2.next_to(self.end_line, DOWN, buff=0.5)
            self.play(Write(l2), run_time=1.8)
        self.wait(1.0)
        self.play(FadeOut(VGroup(self.end_line, l2)), run_time=1.0)
        end = VGroup(T("GPUs & LLM inference", size=48),
                     T("narration: ElevenLabs  ·  animation: Manim", size=24, color=C_GREY)
                     ).arrange(DOWN, buff=0.4)
        self.play(FadeIn(end), run_time=1.0)
        self.wait(1.8)
        self.play(FadeOut(end), run_time=1.0)
