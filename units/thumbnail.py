"""YouTube thumbnail for the processing-units video.

    manim -s -r 2560,1440 --media_dir media units/thumbnail.py ThumbUnits
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import *  # noqa: E402,F403

TILES = [("CPU", "96 cores", C_BLUE), ("GPU", "990 TFLOP/s", C_YELLOW),
         ("TPU", "128×128 array", C_GREEN), ("NPU", "45 TOPS", C_PINK),
         ("LPU", "80 TB/s SRAM", C_ORANGE), ("WSE", "21 PB/s", C_RED),
         ("FPGA", "rewire it", C_PURPLE), ("ASIC", "200 TH/s", C_GOLD),
         ("DPU", "400 Gb/s", C_TEAL)]


class ThumbUnits(Scene):
    def construct(self):
        plane = NumberPlane(
            x_range=[-8, 8, 1], y_range=[-5, 5, 1],
            background_line_style={"stroke_color": C_BLUE, "stroke_width": 1,
                                   "stroke_opacity": 0.12},
            axis_config={"stroke_opacity": 0}, faded_line_ratio=1)
        self.add(plane)
        tiles = VGroup()
        for abbr, num, col in TILES:
            box = RoundedRectangle(width=1.95, height=1.45, corner_radius=0.12)
            box.set_stroke(col, 3).set_fill(col, 0.16)
            a = T(abbr, size=50, color=col)
            n = T(num, size=21, color=C_WHITE)
            VGroup(a, n).arrange(DOWN, buff=0.08).move_to(box)
            tiles.add(VGroup(box, a, n))
        tiles.arrange_in_grid(3, 3, buff=0.2).to_edge(RIGHT, buff=0.45)
        # highlight the GPU tile a touch
        tiles[1][0].set_fill(C_YELLOW, 0.32).set_stroke(C_YELLOW, 4)

        l1 = T("Every AI chip", size=76, color=C_YELLOW)
        l2 = T("explained", size=76, color=C_WHITE)
        l3 = T("with real numbers", size=44, color=C_BLUE)
        txt = VGroup(l1, l2, l3).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        txt.to_edge(LEFT, buff=0.45)
        for m in txt:
            m.set_stroke(BLACK, 10, background=True)
        self.add(tiles, txt)
