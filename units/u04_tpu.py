import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import *  # noqa: E402,F403

N = 5
CS = 0.75


class TPU(VoiceScene):
    def construct(self):
        head = unit_header("TPU", "Tensor Processing Unit · Google", C_GREEN, 3)
        cells = VGroup()
        grid = [[None] * N for _ in range(N)]
        for r in range(N):
            for c in range(N):
                sq = Square(CS * 0.88).set_stroke(C_GREEN, 2).set_fill(C_GREEN, 0.08)
                sq.move_to([c * CS, -r * CS, 0])
                w = Dot(radius=0.06, color=C_GOLD).move_to(sq.get_corner(UR) + DL * 0.14)
                cell = VGroup(sq, w)
                grid[r][c] = cell
                cells.add(cell)
        cells.move_to(LEFT * 2.6 + DOWN * 0.5)
        arr_l = T("multiply-accumulate cells", size=22, color=C_GREEN).next_to(cells, UP, 0.2)
        with self.voiceover(
            "The TPU, Google's Tensor Processing Unit. It isn't a general-purpose chip at all. "
            "It's built around one structure: the systolic array."
        ) as vo:
            self.play(FadeIn(head, shift=RIGHT * 0.2), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(c, scale=0.7) for c in cells], lag_ratio=0.03),
                      FadeIn(arr_l), run_time=1.8)

        with self.voiceover(
            "Picture a 128 by 128 grid of multiply-accumulate cells. Weights sit inside the "
            "cells. Input numbers pulse in from the left, one step per clock, and partial sums "
            "flow down. Every value gets reused across a whole row or column, without ever "
            "going back to memory."
        ) as vo:
            real = T("real chip: 128 × 128 grid", size=22, color=C_GREY).next_to(cells, DOWN, 0.25)
            self.play(FadeIn(real), run_time=0.5)
            wl = T("weights stay put", size=22, color=C_GOLD).next_to(cells, RIGHT, buff=0.4)
            wl.align_to(cells, UP)
            self.play(*[grid[r][c][1].animate.scale(1.6) for r in range(N) for c in range(N)],
                      FadeIn(wl), run_time=0.7)
            self.play(*[grid[r][c][1].animate.scale(1 / 1.6) for r in range(N) for c in range(N)],
                      run_time=0.3)
            # inputs enter from the left, staggered by row (the "pulse")
            ins = VGroup()
            for r in range(N):
                d = Dot(radius=0.11, color=C_PINK)
                d.move_to(grid[r][0][0].get_center() + LEFT * CS * (1 + r))
                ins.add(d)
            in_l = T("inputs →", size=22, color=C_PINK).next_to(ins, LEFT, buff=0.15)
            sum_l = T("sums ↓", size=22, color=C_WHITE).next_to(cells, DOWN, buff=0.7)
            self.play(FadeIn(ins), FadeIn(in_l), FadeOut(real), run_time=0.6)
            steps = 2 * N
            per = max(0.3, (self.remaining(vo) - 1.5) / steps)
            outs = VGroup()
            for t in range(steps):
                anims = [d.animate.shift(RIGHT * CS) for d in ins]
                lit = []
                for r in range(N):
                    c = t - r  # column the row-r input reaches this beat
                    if 0 <= c < N:
                        lit.append(grid[r][c][0])
                anims += [sq.animate.set_fill(C_GREEN, 0.75) for sq in lit]
                self.play(*anims, run_time=per * 0.6, rate_func=linear)
                if lit:
                    self.play(*[sq.animate.set_fill(C_GREEN, 0.08) for sq in lit],
                              run_time=per * 0.4)
                else:
                    self.wait(per * 0.4)
                if t == N - 1:
                    self.play(FadeIn(sum_l), run_time=0.2)
            for c in range(N):
                o = Dot(radius=0.09, color=C_WHITE).move_to(grid[N - 1][c][0].get_bottom())
                outs.add(o)
            self.play(FadeOut(ins), *[o.animate.shift(DOWN * 0.45) for o in outs],
                      FadeIn(outs), run_time=0.6)

        board = spec_board([
            ("197 TFLOP/s", "16-bit math per chip (TPU v5e)", C_GREEN),
            ("16 GB", "HBM memory", C_BLUE),
            ("819 GB/s", "memory bandwidth", C_BLUE),
            ("256 chips", "per pod, wired together", C_GREEN),
        ])
        board.move_to(RIGHT * 3.6 + DOWN * 0.3)
        with self.voiceover(
            "That's why it's efficient: almost no energy goes into fetching data. A TPU v5e chip "
            "delivers 197 teraflops of 16-bit math, with 16 gigabytes of memory at 819 gigabytes "
            "per second."
        ) as vo:
            self.play(FadeOut(VGroup(wl, in_l, sum_l, outs)), run_time=0.5)
            reveal_specs(self, board[:3], run_time=min(3.5, vo.duration - 0.8))

        with self.voiceover(
            "Yardstick: about 100 tokens per second per chip. But TPUs are meant to be used in "
            "pods of up to 256 chips, wired directly to each other."
        ) as vo:
            self.play(FadeOut(VGroup(cells, arr_l)), run_time=0.5)
            ys = yardstick(r"819\ \text{GB/s}", r"100\ \text{tokens/s}", color=C_GREEN)
            ys.move_to(LEFT * 3.3 + UP * 0.9)
            self.play(FadeIn(ys, shift=UP * 0.2), run_time=1.0)
            pod = VGroup(*[Square(0.1).set_stroke(width=0).set_fill(C_GREEN, 0.7)
                           for _ in range(256)]).arrange_in_grid(16, 16, buff=0.035)
            pod.next_to(ys, DOWN, buff=0.45)
            self.play(FadeIn(board[3], shift=LEFT * 0.2),
                      LaggedStart(*[FadeIn(p) for p in pod], lag_ratio=0.004), run_time=1.6)
        self.clear_all(run_time=0.6)
