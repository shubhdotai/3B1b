import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403

USER_COLORS = [C_PINK, C_BLUE, C_GREEN, C_GOLD, C_PURPLE, C_TEAL, C_RED, C_ORANGE]


def user_icon(color, r=0.22):
    head = Circle(r * 0.45).set_stroke(color, 2).set_fill(color, 0.5)
    body = Arc(radius=r * 0.8, start_angle=0, angle=PI).set_stroke(color, 2)
    body.next_to(head, DOWN, buff=0.04)
    return VGroup(head, body)


class Batching(VoiceScene):
    def construct(self):
        self.chapter_card(6, "Batching")
        rng = np.random.default_rng(31)

        with self.voiceover(
            "So how do companies serve millions of people with such hardware? The key "
            "trick is batching."
        ) as vo:
            users = VGroup(*[user_icon(USER_COLORS[i % 8]) for i in range(64)])
            users.arrange_in_grid(rows=4, cols=16, buff=0.3).shift(UP * 0.5)
            self.play(LaggedStart(*[FadeIn(u, shift=DOWN * 0.1) for u in users],
                                  lag_ratio=0.02), run_time=2.2)
            lab = T("many users, each waiting for their next token", size=28, color=C_GREY)
            lab.next_to(users, DOWN, buff=0.5)
            self.play(FadeIn(lab), run_time=0.8)

        B = 8
        W = cell_grid(8, 8, 0.3, COL_WEIGHT, rng.uniform(0.1, 0.9, (8, 8)), stroke=0.8)
        cols = VGroup(*[cell_grid(8, 1, 0.3, USER_COLORS[i], rng.uniform(0.2, 0.9, (8, 1)),
                                  stroke=0.8) for i in range(B)]).arrange(RIGHT, buff=0.04)
        Y = cell_grid(8, B, 0.3, C_WHITE, np.zeros((8, B)), stroke=0.8, min_opacity=0.03)
        eq = VGroup(W, M(r"\times", 36), cols, M("=", 36), Y).arrange(RIGHT, buff=0.22)
        eq.move_to(DOWN * 0.4)
        with self.voiceover(
            "If a hundred different users are each waiting for their next token, the "
            "server can stack their hundred vectors side by side into a matrix. Now each "
            "weight is loaded from memory once, but used a hundred times."
        ) as vo:
            picked = VGroup(*[users[i] for i in range(B)])
            self.play(FadeOut(lab), FadeOut(VGroup(*[u for u in users if u not in picked])),
                      run_time=0.8)
            self.play(FadeIn(W), FadeIn(eq[1]), run_time=0.6)
            self.play(*[ReplacementTransform(u, c) for u, c in zip(picked, cols)],
                      run_time=1.6)
            bl = Brace(cols, DOWN, color=C_GREY)
            bt = T("one vector per user", size=22, color=C_GREY).next_to(bl, DOWN, 0.1)
            self.play(GrowFromCenter(bl), FadeIn(bt), FadeIn(eq[3]), FadeIn(Y),
                      run_time=1.0)
            # one weight row is used against every column
            row = SurroundingRectangle(VGroup(*W.cells[2]), color=C_WHITE, buff=0.02)
            self.play(Create(row), run_time=0.5)
            for c in range(B):
                self.play(Y.cells[2][c].animate.set_fill(C_WHITE, 0.8), run_time=0.18)
            once = T("loaded once,\nused by every user", size=24, color=COL_WEIGHT)
            once.next_to(W, UP, buff=0.3)
            self.play(FadeIn(once), run_time=0.6)
            self.play(LaggedStart(*[Y.cells[r][c].animate.set_fill(C_WHITE,
                                                                   rng.uniform(0.3, 0.9))
                                    for r in range(8) for c in range(B) if r != 2],
                                  lag_ratio=0.005), FadeOut(row), run_time=1.0)

        ax, roof = small_roofline()
        with self.voiceover(
            "Since the time per step was dominated by reading the weights, processing a "
            "hundred users costs barely more than processing one. Throughput grows almost "
            "linearly with batch size, and the point on the roofline slides to the right, "
            "toward the ridge."
        ) as vo:
            self.play(FadeOut(VGroup(eq, bl, bt, once)), run_time=0.6)
            # bar chart of throughput vs batch size
            sizes = [1, 8, 32, 64, 128]
            tput = [210, 1680, 6700, 13000, 24000]
            chart_ax = Axes(x_range=[0, 5.5, 1], y_range=[0, 26000, 5000], x_length=5.6,
                            y_length=3.6, tips=False,
                            axis_config={"color": C_GREY, "include_ticks": False})
            chart_ax.to_edge(LEFT, buff=0.9).shift(DOWN * 0.3)
            bars = VGroup()
            xlabs = VGroup()
            for i, (s, tp) in enumerate(zip(sizes, tput)):
                h = chart_ax.c2p(0, tp)[1] - chart_ax.c2p(0, 0)[1]
                b = Rectangle(width=0.6, height=max(h, 0.03)).set_stroke(width=0).set_fill(
                    C_PINK, 0.85)
                b.move_to(chart_ax.c2p(i + 0.8, 0), aligned_edge=DOWN)
                bars.add(b)
                xlabs.add(T(str(s), size=20, color=C_GREY).next_to(b, DOWN, buff=0.15)
                          .set_y(chart_ax.c2p(0, 0)[1] - 0.25))
            ct = T("tokens / second (all users)", size=22, color=C_PINK)
            ct.next_to(chart_ax, UP, buff=0.2)
            cx = T("batch size", size=22, color=C_GREY).next_to(xlabs, DOWN, buff=0.2)
            step = T("time per step ≈ 5 ms  (almost constant)", size=22, color=C_BLUE)
            step.next_to(cx, DOWN, buff=0.25)
            self.play(Create(chart_ax), FadeIn(ct), FadeIn(cx), FadeIn(roof), run_time=1.2)
            dp = roof_point(ax, 0.0, C_PINK, "batch 1", direction=RIGHT)
            self.play(GrowFromEdge(bars[0], DOWN), FadeIn(xlabs[0]), FadeIn(dp), run_time=0.8)
            self.play(FadeIn(step), run_time=0.6)
            for i in range(1, len(sizes)):
                lx = np.log10(sizes[i])
                new_dp = roof_point(ax, lx, C_PINK, f"batch {sizes[i]}",
                                    direction=RIGHT if lx < 1.9 else DOWN + RIGHT * 0.3)
                self.play(GrowFromEdge(bars[i], DOWN), FadeIn(xlabs[i]),
                          Transform(dp, new_dp), run_time=1.0)
            ridge_dot = Dot(ax.c2p(ax.ridge, ax.perf(ax.ridge)), color=C_WHITE, radius=0.07)
            self.play(FadeIn(ridge_dot), Flash(ridge_dot, color=C_WHITE), run_time=0.8)

        # --- Continuous batching -------------------------------------------
        with self.voiceover(
            "In practice, requests arrive and finish at different times, so modern servers "
            "use continuous batching: at every step, finished sequences leave, and waiting "
            "requests jump into the open slots, keeping the GPU full."
        ) as vo:
            self.clear_all(run_time=0.6)
            title = T("Continuous batching", size=40).to_edge(UP, buff=0.4)
            slots, steps, cs = 6, 22, 0.42
            grid = cell_grid(slots, steps, cs, C_GREY_D, np.zeros((slots, steps)),
                             stroke=0.6, min_opacity=0.0, stroke_color=C_GREY_D)
            grid.shift(DOWN * 0.2 + RIGHT * 0.6)
            sl = VGroup(*[T(f"slot {i + 1}", size=18, color=C_GREY).next_to(
                grid.cells[i][0], LEFT, buff=0.2) for i in range(slots)])
            st = T("decode step →", size=22, color=C_GREY).next_to(grid, DOWN, buff=0.2)
            self.play(Write(title), FadeIn(grid), FadeIn(sl), FadeIn(st), run_time=1.0)
            # simulate requests
            r2 = np.random.default_rng(4)
            color_seq = 0
            plan = []  # (slot, start, length, color)
            for s in range(slots):
                t = 0
                while t < steps:
                    L = int(r2.integers(3, 10))
                    plan.append((s, t, min(L, steps - t), USER_COLORS[color_seq % 8]))
                    color_seq += 1
                    t += L
            col_anims = []
            for step in range(steps):
                anims = []
                for (s, t0, L, col) in plan:
                    if t0 <= step < t0 + L:
                        cell = grid.cells[s][step]
                        anims.append(cell.animate.set_fill(col, 0.85 if step != t0 else 1.0))
                col_anims.append(anims)
            starts = VGroup()
            for (s, t0, L, col) in plan:
                if t0 > 0:
                    m = Triangle(color=WHITE).scale(0.07).rotate(-PI / 2).set_fill(WHITE, 1)
                    m.move_to(grid.cells[s][t0].get_left())
                    starts.add(m)
            per = max(0.12, (self.remaining(vo) - 1.6) / steps)
            cursor = Line(grid.get_top() + UP * 0.1, grid.get_bottom() + DOWN * 0.1,
                          color=C_WHITE, stroke_width=3)
            cursor.next_to(grid.cells[0][0], LEFT, buff=0).match_y(grid)
            self.add(cursor)
            for step in range(steps):
                self.play(*col_anims[step],
                          cursor.animate.next_to(grid.cells[0][step], RIGHT, buff=0).match_y(grid),
                          run_time=per, rate_func=linear)
            self.play(FadeIn(starts), FadeOut(cursor), run_time=0.6)
            note = T("▸ new request joins the moment a slot frees up", size=22, color=C_WHITE)
            note.next_to(st, DOWN, buff=0.2)
            self.play(FadeIn(note), run_time=0.6)

        with self.voiceover(
            "But batching runs into a second memory problem, and to see it, we need to look "
            "inside attention."
        ) as vo:
            self.clear_all(run_time=0.8)
            q = T("Attention", size=60, color=C_BLUE)
            self.play(Write(q), run_time=1.4)
            self.play(q.animate.scale(1.1).set_color(C_GREEN), run_time=1.0)
        self.clear_all()
