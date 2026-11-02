"""Shared pieces for the 'every processing unit' video."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F401,F403

MODEL_GB = 8  # 8B parameters at 8-bit = 8 GB read per generated token


def unit_header(abbr: str, full: str, color, index: int | None = None) -> VGroup:
    a = T(abbr, size=56, color=color)
    f = T(full, size=26, color=C_GREY)
    row = VGroup(a, f).arrange(RIGHT, buff=0.35, aligned_edge=DOWN)
    f.shift(UP * 0.06)
    if index is not None:
        n = Mono(f"{index}/9", size=20, color=C_GREY_D)
        n.next_to(row, RIGHT, buff=0.35).align_to(f, DOWN)
        row.add(n)
    row.to_corner(UL, buff=0.4)
    line = Line(row.get_corner(DL) + DOWN * 0.15, row.get_corner(DL) + DOWN * 0.15 + RIGHT * 13.2,
                color=color, stroke_width=1.5, stroke_opacity=0.5)
    g = VGroup(row, line)
    return g


def spec_board(items, value_size=40, label_size=20, buff=0.32) -> VGroup:
    """items: list of (value, label, color). Values big, labels small and grey."""
    rows = VGroup()
    for value, label, color in items:
        v = T(value, size=value_size, color=color)
        l = T(label, size=label_size, color=C_GREY)
        rows.add(VGroup(v, l).arrange(DOWN, aligned_edge=LEFT, buff=0.08))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=buff)
    return rows


def yardstick(bw: str, result: str, model: str = f"{MODEL_GB}\\ \\text{{GB}}",
              color=C_YELLOW) -> VGroup:
    eq = M(r"\frac{" + bw + r"}{" + model + r"} \approx " + result, 46, C_WHITE)
    tag = T("text speed limit · 8B model at 8-bit", size=20, color=C_GREY)
    box_content = VGroup(eq, tag).arrange(DOWN, buff=0.15)
    box = SurroundingRectangle(box_content, color=color, buff=0.22, corner_radius=0.1,
                               stroke_width=2)
    box.set_fill(BLACK, 0.85)
    return VGroup(box, box_content)


def reveal_specs(scene, board, run_time=2.0):
    scene.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.2) for r in board], lag_ratio=0.35),
               run_time=run_time)
