"""Shared look-and-feel and the narration-synced scene base class."""
from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from manim import *  # noqa: F401,F403

from .tts import ROOT, synthesize

# ---------------------------------------------------------------------------
# Palette (3Blue1Brown-ish)
# ---------------------------------------------------------------------------
BG = "#000000"
C_BLUE = "#58C4DD"
C_BLUE_D = "#236B8E"
C_TEAL = "#5CD0B3"
C_GREEN = "#83C167"
C_YELLOW = "#FFFF00"
C_GOLD = "#F0AC5F"
C_ORANGE = "#FF862F"
C_RED = "#FC6255"
C_PINK = "#D147BD"
C_PURPLE = "#9A72AC"
C_GREY = "#888888"
C_GREY_D = "#444444"
C_WHITE = "#FFFFFF"

# Semantic colors used consistently through the video
COL_COMPUTE = C_YELLOW   # arithmetic units / tensor cores / FLOPs
COL_MEMORY = C_BLUE      # HBM / bytes / bandwidth
COL_SRAM = C_TEAL        # shared memory / registers / on-chip
COL_WEIGHT = C_GOLD      # model weights
COL_TOKEN = C_PINK       # token vectors / activations
COL_KV = C_GREEN         # KV cache

FONT = "CMU Serif"
MONO = "DejaVu Sans Mono"

config.background_color = BG


def T(text: str, size: float = 36, color=C_WHITE, **kw) -> Text:
    """Serif text in the 3b1b style."""
    return Text(text, font=FONT, font_size=size, color=color, **kw)


def M(tex: str, size: float = 40, color=C_WHITE, **kw) -> MathTex:
    return MathTex(tex, font_size=size, color=color, **kw)


def Mono(text: str, size: float = 28, color=C_WHITE, **kw) -> Text:
    return Text(text, font=MONO, font_size=size, color=color, **kw)


# ---------------------------------------------------------------------------
# Little building blocks
# ---------------------------------------------------------------------------
def cell_grid(rows: int, cols: int, size: float = 0.3, color=C_BLUE,
              values=None, stroke=1.0, gap: float = 0.0,
              stroke_color=None, min_opacity: float = 0.08) -> VGroup:
    """A rows x cols grid of squares, optionally shaded like a heat map.

    Cells are stored row-major; ``grid.cells[r][c]`` is also available.
    """
    if values is None:
        values = np.full((rows, cols), 0.5)
    values = np.asarray(values, dtype=float)
    grid = VGroup()
    cells = []
    for r in range(rows):
        row = []
        for c in range(cols):
            sq = Square(side_length=size)
            v = float(np.clip(values[r, c], 0, 1))
            sq.set_fill(color, opacity=min_opacity + (1 - min_opacity) * v)
            sq.set_stroke(stroke_color or color, width=stroke, opacity=0.9)
            sq.move_to(np.array([c * (size + gap), -r * (size + gap), 0]))
            grid.add(sq)
            row.append(sq)
        cells.append(row)
    grid.move_to(ORIGIN)
    grid.cells = cells
    grid.rows, grid.cols = rows, cols
    return grid


def labeled_box(label: str, width: float, height: float, color=C_BLUE,
                size: float = 28, fill_opacity: float = 0.15,
                label_color=None, corner_radius: float = 0.08) -> VGroup:
    box = RoundedRectangle(width=width, height=height, corner_radius=corner_radius)
    box.set_stroke(color, 2).set_fill(color, fill_opacity)
    txt = T(label, size=size, color=label_color or color)
    if txt.width > width * 0.9:
        txt.scale_to_fit_width(width * 0.9)
    txt.move_to(box)
    g = VGroup(box, txt)
    g.box, g.label = box, txt
    return g


def bracket_matrix(entries, color=C_WHITE, size: float = 30, h_buff=0.6, v_buff=0.5):
    m = Matrix(entries, h_buff=h_buff, v_buff=v_buff,
               element_to_mobject=lambda x: T(str(x), size=size, color=color))
    return m


def stream_dots(start, end, n: int = 12, color=COL_MEMORY, radius=0.05):
    """A column of little dots to animate data flowing from start to end."""
    dots = VGroup(*[Dot(radius=radius, color=color) for _ in range(n)])
    for d in dots:
        d.move_to(start)
    return dots


def flow_animation(dots, start, end, run_time=2.0, lag=0.08, path_arc=0):
    anims = []
    for d in dots:
        d.move_to(start)
        anims.append(MoveAlongPath(d, ArcBetweenPoints(start, end, angle=path_arc)
                                   if path_arc else Line(start, end),
                                   rate_func=linear))
    return LaggedStart(*anims, lag_ratio=lag, run_time=run_time)


def underline(mob, color=C_YELLOW, buff=0.08):
    return Line(mob.get_corner(DL) + DOWN * buff, mob.get_corner(DR) + DOWN * buff,
                color=color, stroke_width=3)


# ---------------------------------------------------------------------------
# Narration-synced scene
# ---------------------------------------------------------------------------
TRANSCRIPT_DIR = ROOT / "media" / "transcripts"


class VoiceScene(MovingCameraScene):
    """A scene whose beats are timed to ElevenLabs narration.

    Usage::

        with self.voiceover("Some narration") as vo:
            self.play(Create(x), run_time=vo.duration * 0.5)
        # the context waits out whatever narration is left
    """

    tail_pad = 0.25  # small breath between narration segments

    def setup(self):
        super().setup()
        self._transcript = []
        self._prev_text = None

    class _VO:
        def __init__(self, duration, start):
            self.duration = duration
            self.start = start

    def _now(self) -> float:
        return float(self.renderer.time)

    @contextmanager
    def voiceover(self, text: str, pad: float | None = None):
        text = " ".join(text.split())
        path, dur = synthesize(text, previous_text=self._prev_text)
        self._prev_text = text
        start = self._now()
        self.add_sound(str(path))
        self._transcript.append({"start": start, "duration": dur, "text": text})
        vo = self._VO(dur, start)
        yield vo
        remaining = dur - (self._now() - start)
        pad = self.tail_pad if pad is None else pad
        if remaining + pad > 0.02:
            self.wait(max(remaining, 0) + pad)

    def remaining(self, vo) -> float:
        return max(0.1, vo.duration - (self._now() - vo.start))

    def tear_down(self):
        super().tear_down()
        TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
        out = TRANSCRIPT_DIR / f"{type(self).__name__}.json"
        out.write_text(json.dumps(
            {"scene": type(self).__name__, "total": self._now(),
             "segments": self._transcript}, indent=1))

    # -- common flourishes -------------------------------------------------
    def chapter_card(self, number: int, title: str, run=1.3):
        num = T(f"Chapter {number}", size=30, color=C_GREY)
        ttl = T(title, size=60, color=C_WHITE)
        grp = VGroup(num, ttl).arrange(DOWN, buff=0.35)
        line = Line(LEFT * 3.5, RIGHT * 3.5, color=C_BLUE, stroke_width=2)
        line.next_to(ttl, DOWN, buff=0.35)
        self.play(FadeIn(num, shift=UP * 0.2), Write(ttl), Create(line), run_time=run)
        self.wait(0.4)
        self.play(FadeOut(VGroup(grp, line), shift=UP * 0.3), run_time=0.5)

    def drop(self, *mobs):
        """Remove mobjects *and* all their parts (robust to dissolved groups)."""
        self.remove(*[f for m in mobs for f in m.get_family()])

    def clear_all(self, run_time=0.8):
        mobs = [m for m in self.mobjects if m is not self.camera.frame]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)
