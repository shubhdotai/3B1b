"""YouTube thumbnail stills.

    manim -s -r 2560,1440 --media_dir media scenes/thumbnail.py ThumbIdle
    manim -s -r 2560,1440 --media_dir media scenes/thumbnail.py ThumbEquation
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403


def glow(mob, color, layers=6, max_width=28, opacity=0.06):
    g = VGroup()
    for i in range(layers):
        c = mob.copy().set_fill(opacity=0)
        c.set_stroke(color, width=max_width * (i + 1) / layers, opacity=opacity)
        g.add(c)
    return g


def hero_chip(scale_w=6.4, seed=4):
    chip = gpu_chip(width=scale_w, height=scale_w * 0.66, show_labels=False)
    rng = np.random.default_rng(seed)
    lit = set(rng.choice(len(chip.sms), 9, replace=False).tolist())
    for i, sm in enumerate(chip.sms):
        if i in lit:
            sm.set_fill(C_YELLOW, 0.95).set_stroke(C_YELLOW, 1.5, opacity=1)
        else:
            sm.set_fill(C_YELLOW, 0.06).set_stroke(C_YELLOW, 1, opacity=0.35)
    chip.hbm.set_fill(C_BLUE, 0.85).set_stroke(C_BLUE, 3)
    chip.l2.set_fill(C_BLUE, 0.3)
    halo = VGroup(*[glow(h, C_BLUE, layers=7, max_width=60, opacity=0.05) for h in chip.hbm])
    # one clean stream of weights from each HBM stack toward the compute
    streams = VGroup()
    center = chip.die.get_center()
    for h in chip.hbm:
        a = h.get_center()
        b = center + (a - center) * 0.42
        beam = Line(a, b, stroke_width=10, color=COL_WEIGHT, stroke_opacity=0.18)
        streams.add(beam)
        n = 7
        for j in range(n):
            t = j / (n - 1)
            streams.add(Dot(interpolate(a, b, t), radius=0.06 * (1 - 0.45 * t),
                            color=COL_WEIGHT).set_opacity(1 - 0.6 * t))
    return VGroup(halo, chip, streams), chip


def faint_grid():
    plane = NumberPlane(
        x_range=[-8, 8, 1], y_range=[-5, 5, 1],
        background_line_style={"stroke_color": C_BLUE, "stroke_width": 1, "stroke_opacity": 0.12},
        axis_config={"stroke_opacity": 0},
        faded_line_ratio=1,
    )
    return plane


class ThumbIdle(Scene):
    def construct(self):
        self.add(faint_grid())
        art, chip = hero_chip(scale_w=5.0)
        art.move_to(RIGHT * 3.6 + DOWN * 0.1)
        self.add(art)

        big = T("99% idle", size=118, color=C_YELLOW)
        sub = T("waiting on memory", size=54, color=C_BLUE)
        txt = VGroup(big, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        txt.to_edge(LEFT, buff=0.5).shift(UP * 0.35)
        for m in (big, sub):
            m.set_stroke(BLACK, 10, background=True)
        small = T("How GPUs actually run LLMs", size=30, color=C_GREY)
        small.next_to(txt, DOWN, buff=0.6, aligned_edge=LEFT)
        self.add(txt, small)


class ThumbEquation(Scene):
    def construct(self):
        self.add(faint_grid())
        art, chip = hero_chip(scale_w=5.6)
        art.move_to(RIGHT * 3.4 + DOWN * 0.9)
        self.add(art)
        eq = M(r"\text{time per token} \approx "
               r"\frac{\text{bytes moved}}{\text{bandwidth}}", 82)
        eq[0][13:23].set_color(C_GOLD)
        eq[0][24:].set_color(C_BLUE)
        eq.to_edge(UP, buff=0.55)
        eq.set_stroke(BLACK, 8, background=True)
        tag = VGroup(T("It's not", size=78, color=C_WHITE),
                     T("the math.", size=78, color=C_YELLOW)).arrange(DOWN, aligned_edge=LEFT,
                                                                      buff=0.15)
        tag.to_edge(LEFT, buff=0.6).shift(DOWN * 1.1)
        self.add(eq, tag)
