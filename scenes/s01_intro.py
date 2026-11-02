import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403

TOKEN_COLORS = [C_BLUE, C_TEAL, C_GREEN, C_GOLD, C_PINK, C_PURPLE, C_RED]


def token_row(words, size=30, start_color=0):
    boxes = VGroup()
    for i, w in enumerate(words):
        txt = T(w, size=size)
        col = TOKEN_COLORS[(i + start_color) % len(TOKEN_COLORS)]
        bg = SurroundingRectangle(txt, buff=0.07, corner_radius=0.05)
        bg.set_stroke(col, 1.5).set_fill(col, 0.25)
        bg.stretch_to_fit_height(0.52)
        txt.move_to(bg)
        boxes.add(VGroup(bg, txt))
    boxes.arrange(RIGHT, buff=0.06)
    return boxes


class Intro(VoiceScene):
    def construct(self):
        # --- Chat window ----------------------------------------------------
        window = RoundedRectangle(width=11.5, height=3.8, corner_radius=0.2)
        window.set_stroke(C_GREY, 2).set_fill("#0c0d10", 1)
        prompt = T("How does a GPU run a language model?", size=30, color=C_WHITE)
        prompt.move_to(window.get_top() + DOWN * 0.75).align_to(window, LEFT).shift(
            RIGHT * 1.6)
        you = T("You", size=24, color=C_GREY).next_to(prompt, LEFT, buff=0.3)
        prompt_row = VGroup(you, prompt)
        words1 = ["It", " streams", " weights", " from", " memory", ","]
        words2 = [" one", " token", " at", " a", " time", "..."]
        row1 = token_row(words1)
        row2 = token_row(words2, start_color=len(words1))
        rows = VGroup(row1, row2).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        rows.next_to(prompt, DOWN, buff=0.6).align_to(prompt, LEFT)
        model_lab = T("Model", size=24, color=C_GREY).next_to(row1, LEFT, buff=0.3)
        cursor = Rectangle(width=0.06, height=0.45).set_fill(C_WHITE, 1).set_stroke(width=0)

        all_tokens = [*row1, *row2]
        with self.voiceover(
            "When you ask a large language model a question, the answer appears "
            "one word at a time, almost like someone is typing it."
        ) as vo:
            self.play(FadeIn(window), run_time=0.6)
            self.play(Write(prompt_row), run_time=1.2)
            self.play(FadeIn(model_lab), run_time=0.3)
            per = (vo.duration - 2.3) / len(all_tokens)
            for tok in all_tokens:
                cursor.next_to(tok, RIGHT, buff=0.05)
                self.add(cursor)
                self.play(FadeIn(tok, shift=RIGHT * 0.05), run_time=per * 0.6)
                self.wait(per * 0.4)
            self.remove(cursor)

        # --- Each token is a huge computation --------------------------------
        target = row1[2]
        with self.voiceover(
            "Each of those little pieces of text, called tokens, is the output of an "
            "enormous computation: billions of multiplications, carried out on a "
            "chip called a GPU."
        ) as vo:
            others = VGroup(*[t for t in all_tokens if t is not target])
            self.play(others.animate.set_opacity(0.25),
                      Indicate(target, color=C_YELLOW, scale_factor=1.15),
                      run_time=1.2)
            chip = gpu_chip(width=4.2, height=2.8, show_labels=False)
            chip.scale(0.85).to_edge(DOWN, buff=0.25).shift(RIGHT * 3.0)
            nums = VGroup()
            rng = np.random.default_rng(0)
            for i in range(30):
                a, b = rng.uniform(-1, 1, 2)
                nums.add(T(f"{a:+.2f}×{b:+.2f}", size=16, color=C_YELLOW))
            nums.arrange_in_grid(rows=5, cols=6, buff=(0.15, 0.08))
            nums.next_to(chip, LEFT, buff=0.4)
            self.play(
                VGroup(window, prompt_row, model_lab, rows).animate.scale(0.75).to_edge(
                    UP, buff=0.3),
                run_time=1.0,
            )
            self.play(FadeIn(chip, shift=UP * 0.3), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(n, scale=0.6) for n in nums], lag_ratio=0.04),
                      run_time=min(2.2, self.remaining(vo) - 0.3))
            arrow = Arrow(chip.get_top(), target.get_bottom(), color=C_YELLOW, buff=0.15,
                          stroke_width=4)
            self.play(GrowArrow(arrow), run_time=0.6)

        # --- What this video covers -----------------------------------------
        with self.voiceover(
            "In this video, let's open up that chip: from how the hardware is organized, "
            "all the way up to the tricks that make modern chatbots fast."
        ) as vo:
            self.play(FadeOut(VGroup(window, prompt_row, model_lab, rows, nums, arrow)),
                      run_time=0.8)
            self.play(chip.animate.scale(1.9).move_to(UP * 0.3), run_time=1.4)
            lbls = hbm_labels(chip, size=22)
            self.play(FadeIn(lbls), run_time=0.5)
            topics = VGroup(
                T("Architecture", size=28, color=C_YELLOW),
                T("Memory hierarchy", size=28, color=C_BLUE),
                T("Prefill & decode", size=28, color=C_PINK),
                T("Batching · KV cache · FlashAttention", size=28, color=C_GREEN),
            ).arrange(RIGHT, buff=0.5).scale_to_fit_width(13).to_edge(DOWN, buff=0.35)
            self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in topics],
                                  lag_ratio=0.45), run_time=self.remaining(vo) * 0.8)

        # --- The surprise: memory is the bottleneck ---------------------------
        with self.voiceover(
            "And along the way we'll run into a surprising fact. For most of the time "
            "a GPU spends generating text, the bottleneck is not the math. The "
            "arithmetic units sit mostly idle. The real limit is something much more "
            "mundane: how quickly you can move numbers out of memory."
        ) as vo:
            self.play(FadeOut(topics), run_time=0.5)
            # pulse the compute units, then dim them ("idle")
            self.play(chip.sms.animate.set_fill(C_YELLOW, 0.85), run_time=0.8)
            self.wait(1.6)
            idle_t = T("idle", size=40, color=C_YELLOW)
            idle_bg = BackgroundRectangle(idle_t, color=BLACK, fill_opacity=0.85, buff=0.15)
            idle = VGroup(idle_bg, idle_t).move_to(chip.die).shift(UP * 1.4)
            self.play(chip.sms.animate.set_fill(C_YELLOW, 0.08), FadeIn(idle), run_time=1.4)
            self.wait(1.5)
            # data trickling from HBM
            flows = []
            dots_all = VGroup()
            for st in chip.hbm:
                start = st.get_center()
                end = chip.die.get_center() + (start - chip.die.get_center()) * 0.25
                dots = stream_dots(start, end, n=8)
                dots_all.add(*dots)
                flows.append(flow_animation(dots, start, end, run_time=2.4, lag=0.12))
            mem_lab = T("Memory bandwidth", size=36, color=C_BLUE)
            mem_lab.next_to(chip, DOWN, buff=0.35)
            self.play(chip.hbm.animate.set_fill(C_BLUE, 0.8), Write(mem_lab), *flows,
                      run_time=2.4)
            self.play(FadeOut(dots_all), run_time=0.3)

        with self.voiceover(
            "To see why, let's start with a more basic question. What even makes a GPU "
            "different from the CPU in your laptop?"
        ) as vo:
            self.play(FadeOut(VGroup(idle, mem_lab, lbls)), run_time=0.6)
            self.play(chip.animate.scale(0.55).shift(RIGHT * 3.4), run_time=1.0)
            cpu = VGroup()
            die = RoundedRectangle(width=3.0, height=3.0, corner_radius=0.1)
            die.set_stroke(C_GREY, 2).set_fill("#111418", 1)
            cores = VGroup(*[Square(0.95).set_stroke(C_BLUE, 2).set_fill(C_BLUE, 0.3)
                             for _ in range(4)]).arrange_in_grid(2, 2, buff=0.25)
            cores.move_to(die)
            cpu.add(die, cores).move_to(LEFT * 3.4 + UP * 0.3)
            cpu_l = T("CPU", size=40, color=C_BLUE).next_to(cpu, DOWN, buff=0.35)
            gpu_l = T("GPU", size=40, color=C_YELLOW).next_to(chip, DOWN, buff=0.35)
            gpu_l.match_y(cpu_l)
            vs = T("vs", size=36, color=C_GREY).move_to((cpu.get_center() + chip.get_center()) / 2)
            self.play(FadeIn(cpu, shift=RIGHT * 0.3), Write(cpu_l), Write(gpu_l),
                      FadeIn(vs), run_time=1.4)
        self.clear_all()
