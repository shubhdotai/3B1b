"""Reusable drawings: the H100 die, one SM, and the roofline plot."""
from __future__ import annotations

import numpy as np
from manim import *  # noqa: F401,F403

from .base import (C_BLUE, C_GREY, C_GREY_D, C_TEAL, C_WHITE, C_YELLOW, C_GOLD, C_PURPLE, C_ORANGE,
                   COL_COMPUTE, COL_MEMORY, COL_SRAM, T, labeled_box)

# H100 SXM numbers used throughout
H100 = dict(sms=132, l2_mb=50, hbm_gb=80, bw_tbs=3.35, bf16_tflops=989)


def gpu_chip(width: float = 7.0, height: float = 4.6, show_labels=True) -> VGroup:
    """Stylised GH100 die with 8 GPCs x 18 SMs (132 enabled), L2 and HBM."""
    chip = VGroup()
    die = RoundedRectangle(width=width, height=height, corner_radius=0.12)
    die.set_stroke(C_GREY, 2).set_fill("#111418", 1)
    chip.add(die)

    l2_h = height * 0.13
    l2 = Rectangle(width=width * 0.92, height=l2_h)
    l2.set_stroke(C_BLUE, 1.5).set_fill(C_BLUE, 0.25).move_to(die)
    chip.add(l2)

    gpc_w = width * 0.92 / 4
    gpc_h = (height - l2_h) / 2 * 0.86
    gpcs, sms = VGroup(), VGroup()
    disabled = set()
    rng = np.random.default_rng(3)
    for idx in rng.choice(144, 12, replace=False):
        disabled.add(int(idx))
    k = 0
    for half, sgn in enumerate([1, -1]):
        for g in range(4):
            gx = die.get_left()[0] + width * 0.04 + gpc_w * (g + 0.5)
            gy = die.get_center()[1] + sgn * (l2_h / 2 + gpc_h / 2 + height * 0.025)
            frame = Rectangle(width=gpc_w * 0.94, height=gpc_h)
            frame.set_stroke(C_GREY_D, 1).set_fill(opacity=0).move_to([gx, gy, 0])
            cols, rows = 6, 3
            cw = frame.width * 0.94 / cols
            chh = frame.height * 0.92 / rows
            g_sms = VGroup()
            for r in range(rows):
                for c in range(cols):
                    sq = Rectangle(width=cw * 0.82, height=chh * 0.82)
                    on = k not in disabled
                    col = C_YELLOW if on else C_GREY_D
                    sq.set_stroke(col, 1, opacity=0.9 if on else 0.5)
                    sq.set_fill(col, 0.28 if on else 0.08)
                    sq.move_to(frame.get_corner(UL) + np.array(
                        [frame.width * 0.03 + cw * (c + 0.5),
                         -frame.height * 0.04 - chh * (r + 0.5), 0]))
                    sq.enabled = on
                    g_sms.add(sq)
                    if on:
                        sms.add(sq)
                    k += 1
            gpcs.add(VGroup(frame, g_sms))
    chip.add(gpcs)

    hbm = VGroup()
    for side in [LEFT, RIGHT]:
        for j in range(3):
            st = RoundedRectangle(width=0.75, height=height / 3.4, corner_radius=0.06)
            st.set_stroke(C_BLUE, 2).set_fill(C_BLUE, 0.35)
            st.next_to(die, side, buff=0.18)
            st.shift(UP * (j - 1) * height / 3.1)
            hbm.add(st)
    chip.add(hbm)

    chip.die, chip.l2, chip.gpcs, chip.sms, chip.hbm = die, l2, gpcs, sms, hbm
    if show_labels:
        l2_lab = T("L2 cache · 50 MB", size=20, color=C_BLUE).move_to(l2)
        chip.l2_label = l2_lab
        chip.add(l2_lab)
    return chip


def hbm_labels(chip, size=20):
    labs = VGroup()
    for side, idx in [(LEFT, 0), (RIGHT, 3)]:
        lab = T("HBM", size=size, color=C_BLUE)
        lab.next_to(chip.hbm[idx + 2], UP, buff=0.12)
        labs.add(lab)
    return labs


def sm_quadrant(width=4.4, height=2.9) -> VGroup:
    q = VGroup()
    frame = RoundedRectangle(width=width, height=height, corner_radius=0.08)
    frame.set_stroke(C_GREY, 1.5).set_fill("#101215", 0)
    q.add(frame)
    sched = labeled_box("Warp scheduler", width * 0.92, height * 0.13, color=C_PURPLE,
                        size=18)
    sched.move_to(frame.get_top() + DOWN * height * 0.11)
    regs = labeled_box("Register file · 64 KB", width * 0.92, height * 0.14,
                       color=COL_SRAM, size=18)
    regs.next_to(sched, DOWN, buff=height * 0.04)
    cores = VGroup()
    for i in range(32):
        sq = Square(side_length=width * 0.055)
        sq.set_stroke(COL_COMPUTE, 1).set_fill(COL_COMPUTE, 0.35)
        cores.add(sq)
    cores.arrange_in_grid(rows=4, cols=8, buff=width * 0.012)
    cores.next_to(regs, DOWN, buff=height * 0.07).align_to(regs, LEFT).shift(
        RIGHT * width * 0.02)
    tensor = labeled_box("Tensor\nCore", width * 0.34, cores.height, color=C_ORANGE,
                         size=20, fill_opacity=0.3)
    tensor.next_to(cores, RIGHT, buff=width * 0.06)
    q.add(sched, regs, cores, tensor)
    q.frame, q.sched, q.regs, q.cores, q.tensor = frame, sched, regs, cores, tensor
    return q


def sm_detail(width=9.6, height=6.8) -> VGroup:
    sm = VGroup()
    outer = RoundedRectangle(width=width, height=height, corner_radius=0.15)
    outer.set_stroke(C_YELLOW, 2.5).set_fill("#0a0b0d", 1)
    title = T("Streaming Multiprocessor (SM)", size=26, color=C_YELLOW)
    title.next_to(outer.get_top(), DOWN, buff=0.15)
    qw, qh = width * 0.47, height * 0.36
    quads = VGroup(*[sm_quadrant(qw, qh) for _ in range(4)])
    quads.arrange_in_grid(rows=2, cols=2, buff=width * 0.02)
    quads.next_to(title, DOWN, buff=0.15)
    smem = labeled_box("L1 / Shared memory · 256 KB", width * 0.96, height * 0.1,
                       color=COL_SRAM, size=22, fill_opacity=0.25)
    smem.next_to(quads, DOWN, buff=0.12)
    sm.add(outer, title, quads, smem)
    sm.outer, sm.title, sm.quads, sm.smem = outer, title, quads, smem
    return sm


def roofline_axes(width=8.0, height=4.8):
    """Log-log roofline for an H100: returns (axes, labels, curve, helpers)."""
    ax = Axes(
        x_range=[0, 4, 1], y_range=[0, 3.5, 1],
        x_length=width, y_length=height,
        axis_config={"color": C_GREY, "include_ticks": True, "stroke_width": 2},
        tips=False,
    )
    xt = VGroup()
    for i, s in enumerate(["1", "10", "100", "1,000", "10,000"]):
        t = T(s, size=18, color=C_GREY).next_to(ax.c2p(i, 0), DOWN, buff=0.15)
        xt.add(t)
    yt = VGroup()
    for i, s in enumerate(["1", "10", "100", "1,000"]):
        t = T(s, size=18, color=C_GREY).next_to(ax.c2p(0, i), LEFT, buff=0.15)
        yt.add(t)
    xl = T("Arithmetic intensity  (FLOPs per byte)", size=22, color=C_WHITE)
    xl.next_to(ax.x_axis, DOWN, buff=0.55)
    yl = T("TFLOP/s achieved", size=22, color=C_WHITE).rotate(PI / 2)
    yl.next_to(ax.y_axis, LEFT, buff=0.6)

    bw, peak = H100["bw_tbs"], H100["bf16_tflops"]
    ridge = np.log10(peak / bw)

    def perf(lx):
        return min(np.log10(bw) + lx, np.log10(peak))

    slope = Line(ax.c2p(0, perf(0)), ax.c2p(ridge, perf(ridge)), color=COL_MEMORY,
                 stroke_width=5)
    flat = Line(ax.c2p(ridge, perf(ridge)), ax.c2p(4, perf(4)), color=COL_COMPUTE,
                stroke_width=5)
    labels = VGroup(xt, yt, xl, yl)
    ax.perf = perf
    ax.ridge = ridge
    return ax, labels, VGroup(slope, flat)


def small_roofline():
    ax, labels, (slope, flat) = roofline_axes(width=5.4, height=3.4)
    xt, yt, xl, yl = labels
    xl.become(T("FLOPs per byte", size=20).next_to(ax.x_axis, DOWN, buff=0.45))
    yl.become(T("TFLOP/s", size=20).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.5))
    for t in [*xt, *yt]:
        t.scale(0.85)
    grp = VGroup(ax, labels, slope, flat)
    grp.to_edge(RIGHT, buff=0.4).shift(DOWN * 0.4)
    return ax, grp


def roof_point(ax, lx, color, label, direction=UP):
    p = ax.c2p(lx, ax.perf(lx))
    dot = Dot(p, radius=0.11, color=color).set_stroke(BLACK, 2)
    lab = T(label, size=24, color=color).next_to(dot, direction, buff=0.15)
    return VGroup(dot, lab)
