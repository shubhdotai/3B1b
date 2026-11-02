import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403


def cpu_core(w=1.5, h=1.5):
    frame = RoundedRectangle(width=w, height=h, corner_radius=0.06)
    frame.set_stroke(C_BLUE, 2).set_fill("#101418", 1)
    ctrl = Rectangle(width=w * 0.86, height=h * 0.3).set_stroke(C_PURPLE, 1.5).set_fill(
        C_PURPLE, 0.35)
    alu = Rectangle(width=w * 0.4, height=h * 0.25).set_stroke(C_YELLOW, 1.5).set_fill(
        C_YELLOW, 0.4)
    alu2 = alu.copy()
    cache = Rectangle(width=w * 0.86, height=h * 0.25).set_stroke(C_BLUE, 1.5).set_fill(
        C_BLUE, 0.35)
    alus = VGroup(alu, alu2).arrange(RIGHT, buff=w * 0.06)
    inner = VGroup(ctrl, alus, cache).arrange(DOWN, buff=h * 0.05).move_to(frame)
    core = VGroup(frame, ctrl, alus, cache)
    core.ctrl, core.alus, core.cache = ctrl, alus, cache
    return core


class CpuVsGpu(VoiceScene):
    def construct(self):
        self.chapter_card(1, "CPU vs GPU")

        # --- CPU -----------------------------------------------------------
        cpu_die = RoundedRectangle(width=5.6, height=5.0, corner_radius=0.12)
        cpu_die.set_stroke(C_GREY, 2).set_fill("#0c0d10", 1)
        cores = VGroup(*[cpu_core() for _ in range(8)]).arrange_in_grid(2, 4, buff=0.12)
        l3 = labeled_box("Shared cache", 5.2, 1.0, color=C_BLUE, size=24, fill_opacity=0.3)
        l3.next_to(cores, DOWN, buff=0.2)
        VGroup(cores, l3).move_to(cpu_die)
        cpu = VGroup(cpu_die, cores, l3).move_to(LEFT * 3.4 + DOWN * 0.2)
        cpu_title = T("CPU", size=44, color=C_BLUE).next_to(cpu, UP, buff=0.25)

        legend = VGroup(
            VGroup(Square(0.25).set_fill(C_PURPLE, 0.6).set_stroke(C_PURPLE, 1),
                   T("control logic", size=22)).arrange(RIGHT, buff=0.15),
            VGroup(Square(0.25).set_fill(C_YELLOW, 0.6).set_stroke(C_YELLOW, 1),
                   T("arithmetic", size=22)).arrange(RIGHT, buff=0.15),
            VGroup(Square(0.25).set_fill(C_BLUE, 0.6).set_stroke(C_BLUE, 1),
                   T("cache", size=22)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(cpu, RIGHT, buff=0.6).shift(UP)

        feats = VGroup(
            T("predict branches", size=26, color=C_PURPLE),
            T("reorder instructions", size=26, color=C_PURPLE),
            T("big caches", size=26, color=C_BLUE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(legend, DOWN, buff=0.6,
                                                               aligned_edge=LEFT)

        with self.voiceover(
            "A CPU is a brilliant generalist: a handful of very powerful cores, each "
            "surrounded by large caches and clever control logic that predicts branches, "
            "reorders instructions, and does everything it can to finish a single stream "
            "of work as fast as possible."
        ) as vo:
            self.play(FadeIn(cpu_die), Write(cpu_title), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in cores], lag_ratio=0.12),
                      FadeIn(l3), run_time=1.6)
            self.play(FadeIn(legend, shift=LEFT * 0.2), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.2) for f in feats],
                                  lag_ratio=0.5), run_time=2.4)
            # a single fast instruction stream through one core
            core0 = cores[0]
            start = core0.get_top() + UP * 0.9
            end = core0.get_bottom() + DOWN * 0.1
            dots = stream_dots(start, end, n=10, color=C_WHITE, radius=0.06)
            self.play(Indicate(core0, color=C_WHITE, scale_factor=1.08), run_time=0.8)
            self.play(flow_animation(dots, start, core0.alus.get_center(), run_time=2.0,
                                     lag=0.1), run_time=2.0)
            self.play(FadeOut(dots), run_time=0.3)

        # --- GPU -----------------------------------------------------------
        gpu_die = RoundedRectangle(width=5.6, height=5.0, corner_radius=0.12)
        gpu_die.set_stroke(C_GREY, 2).set_fill("#0c0d10", 1)
        tiny = VGroup(*[Square(0.115).set_stroke(C_YELLOW, 0.6).set_fill(C_YELLOW, 0.45)
                        for _ in range(40 * 36)])
        tiny.arrange_in_grid(rows=36, cols=40, buff=0.017).move_to(gpu_die)
        gpu = VGroup(gpu_die, tiny).move_to(RIGHT * 3.4 + DOWN * 0.2)
        gpu_title = T("GPU", size=44, color=C_YELLOW).next_to(gpu, UP, buff=0.25)

        with self.voiceover(
            "A GPU makes the opposite bet. It strips each core down to little more than "
            "an arithmetic unit, and then packs in thousands of them. Any one of these "
            "cores is slow and simple, but together they have enormous throughput."
        ) as vo:
            self.play(FadeOut(VGroup(legend, feats)), run_time=0.6)
            self.play(FadeIn(gpu_die), Write(gpu_title), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(t) for t in tiny], lag_ratio=0.002),
                      run_time=2.6)
            lab = T("thousands of simple cores", size=28, color=C_YELLOW)
            lab.next_to(gpu, DOWN, buff=0.25)
            lab2 = T("a few powerful cores", size=28, color=C_BLUE)
            lab2.next_to(cpu, DOWN, buff=0.25)
            self.play(Write(lab2), Write(lab), run_time=1.4)
            self.play(tiny.animate.set_fill(C_YELLOW, 0.9), run_time=0.8)
            self.play(tiny.animate.set_fill(C_YELLOW, 0.45), run_time=0.8)

        # --- Analogy: professors vs stadium ----------------------------------
        with self.voiceover(
            "Think of it as a few brilliant professors versus a stadium full of students "
            "who each know how to multiply and add. For a hard, sequential problem, you "
            "want the professors. For millions of independent little calculations, the "
            "stadium wins by a landslide."
        ) as vo:
            self.play(FadeOut(VGroup(cpu, gpu, lab, lab2)),
                      cpu_title.animate.to_edge(UP, buff=0.3).shift(LEFT * 0.0),
                      gpu_title.animate.to_edge(UP, buff=0.3), run_time=0.8)
            profs = VGroup(*[
                VGroup(Circle(0.42).set_stroke(C_BLUE, 3).set_fill(C_BLUE, 0.25),
                       M(r"\int", size=60, color=C_BLUE))
                for _ in range(4)]).arrange_in_grid(2, 2, buff=0.35)
            profs.next_to(cpu_title, DOWN, buff=0.4)
            studs = VGroup(*[Dot(radius=0.07, color=C_YELLOW) for _ in range(24 * 10)])
            studs.arrange_in_grid(rows=10, cols=24, buff=0.1)
            studs.next_to(gpu_title, DOWN, buff=0.4)
            self.play(LaggedStart(*[GrowFromCenter(p) for p in profs], lag_ratio=0.2),
                      LaggedStart(*[FadeIn(s) for s in studs], lag_ratio=0.003),
                      run_time=2.0)
            # Tasks
            tasks_cpu = VGroup(*[Square(0.16).set_stroke(C_GREY, 0.8).set_fill(C_GREY_D, 0.5)
                                 for _ in range(10 * 16)])
            tasks_cpu.arrange_in_grid(rows=10, cols=16, buff=0.04)
            tasks_cpu.next_to(profs, DOWN, buff=0.4)
            tasks_gpu = tasks_cpu.copy().next_to(studs, DOWN, buff=0.4).match_y(tasks_cpu)
            task_lab = T("many small, independent tasks", size=26, color=C_GREY)
            task_lab.to_edge(DOWN, buff=0.2)
            self.play(FadeIn(tasks_cpu), FadeIn(tasks_gpu), FadeIn(task_lab), run_time=1.0)
            # CPU does 4 at a time, GPU does all at once
            gpu_fill = tasks_gpu.animate.set_fill(C_YELLOW, 0.8).set_stroke(C_YELLOW)
            batches = [tasks_cpu[i:i + 4] for i in range(0, len(tasks_cpu), 4)]
            budget = max(2.0, self.remaining(vo) - 0.6)
            n_show = min(len(batches), int(budget / 0.12))
            self.play(gpu_fill, run_time=0.6)
            done = T("done!", size=30, color=C_YELLOW).next_to(tasks_gpu, RIGHT, buff=0.2)
            self.play(FadeIn(done), run_time=0.3)
            for b in batches[:n_show]:
                self.play(b.animate.set_fill(C_BLUE, 0.8).set_stroke(C_BLUE), run_time=0.1,
                          rate_func=linear)

        # --- Matrix multiplication ----------------------------------------
        with self.voiceover(
            "And it just so happens that the core operation of neural networks is "
            "exactly that kind of problem: matrix multiplication."
        ) as vo:
            self.clear_all(run_time=0.7)
            title = T("Matrix multiplication", size=48).to_edge(UP, buff=0.4)
            self.play(Write(title), run_time=1.2)
            rng = np.random.default_rng(1)
            A = cell_grid(5, 6, 0.5, C_BLUE, rng.uniform(0.1, 0.9, (5, 6)))
            B = cell_grid(6, 5, 0.5, C_PINK, rng.uniform(0.1, 0.9, (6, 5)))
            Cm = cell_grid(5, 5, 0.5, C_YELLOW, np.zeros((5, 5)), min_opacity=0.04)
            eq = VGroup(A, M(r"\times", 48), B, M("=", 48), Cm).arrange(RIGHT, buff=0.35)
            eq.shift(DOWN * 0.3)
            la = M("A", 40, C_BLUE).next_to(A, UP, buff=0.2)
            lb = M("B", 40, C_PINK).next_to(B, UP, buff=0.2)
            lc = M("C", 40, C_YELLOW).next_to(Cm, UP, buff=0.2)
            self.play(FadeIn(eq, shift=UP * 0.2), FadeIn(VGroup(la, lb, lc)),
                      run_time=self.remaining(vo) * 0.8)

        with self.voiceover(
            "Each entry of the output is a dot product between one row of the first "
            "matrix and one column of the second. Crucially, no entry depends on any "
            "other. So you can hand each one to a different worker, and compute them "
            "all at the same time."
        ) as vo:
            def highlight(i, j):
                row = SurroundingRectangle(VGroup(*A.cells[i]), color=C_WHITE, buff=0.03)
                col = SurroundingRectangle(VGroup(*[B.cells[r][j] for r in range(6)]),
                                           color=C_WHITE, buff=0.03)
                cell = SurroundingRectangle(Cm.cells[i][j], color=C_WHITE, buff=0.03)
                return row, col, cell

            dot_eq = M(r"C_{ij} = \sum_k A_{ik}\, B_{kj}", 40).next_to(eq, DOWN, buff=0.6)
            for n, (i, j) in enumerate([(0, 0), (1, 3), (3, 2)]):
                row, col, cell = highlight(i, j)
                anims = [Create(row), Create(col), Create(cell)]
                if n == 0:
                    anims.append(Write(dot_eq))
                self.play(*anims, run_time=0.9)
                self.play(Cm.cells[i][j].animate.set_fill(C_YELLOW, 0.85), run_time=0.5)
                self.play(FadeOut(VGroup(row, col, cell)), run_time=0.4)
            workers = T("every entry, in parallel", size=30, color=C_YELLOW)
            workers.next_to(dot_eq, DOWN, buff=0.35)
            self.play(Write(workers), run_time=1.0)
            vals = np.random.default_rng(2).uniform(0.3, 1.0, (5, 5))
            self.play(LaggedStart(*[
                Cm.cells[r][c].animate.set_fill(C_YELLOW, vals[r, c])
                for r in range(5) for c in range(5)], lag_ratio=0.01),
                run_time=1.2)

        # --- Pixels <-> matrices ---------------------------------------------
        with self.voiceover(
            "This is the whole reason GPUs, originally built to color in pixels for "
            "video games, ended up powering the AI revolution. Shading millions of "
            "pixels and multiplying giant matrices turn out to be the same kind of job."
        ) as vo:
            self.play(FadeOut(VGroup(title, A, B, eq[1], eq[3], la, lb, dot_eq, workers)),
                      VGroup(Cm, lc).animate.move_to(RIGHT * 3.2), run_time=1.0)
            # a little shaded "pixel image": a sphere gradient
            n = 16
            pix = VGroup()
            for r in range(n):
                for c in range(n):
                    x, y = (c - n / 2 + 0.5) / (n / 2), (r - n / 2 + 0.5) / (n / 2)
                    d = x * x + y * y
                    if d < 0.85:
                        z = np.sqrt(0.85 - d)
                        lum = np.clip(0.2 + 0.8 * (-0.5 * x + 0.6 * -y + 0.6 * z), 0.05, 1)
                        col = interpolate_color(ManimColor("#1a2a6c"), ManimColor(C_BLUE), lum)
                    else:
                        col = ManimColor("#151515")
                    sq = Square(0.24).set_stroke(width=0).set_fill(col, 1)
                    sq.move_to([c * 0.25, -r * 0.25, 0])
                    pix.add(sq)
            pix.move_to(LEFT * 3.2)
            pix_l = T("Pixels", size=34, color=C_BLUE).next_to(pix, UP, buff=0.3)
            lc2 = T("Matrix entries", size=34, color=C_YELLOW).next_to(Cm, UP, buff=0.3)
            self.play(LaggedStart(*[FadeIn(p) for p in pix], lag_ratio=0.003),
                      Write(pix_l), ReplacementTransform(lc, lc2), run_time=2.4)
            same = T("same kind of job:  many independent, identical calculations", size=28)
            same.to_edge(DOWN, buff=0.6)
            arrow = DoubleArrow(pix.get_right(), Cm.get_left(), buff=0.3, color=C_WHITE)
            self.play(GrowFromCenter(arrow), Write(same), run_time=1.6)
        self.clear_all()
