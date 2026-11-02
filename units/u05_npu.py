import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import *  # noqa: E402,F403


class NPU(VoiceScene):
    def construct(self):
        head = unit_header("NPU", "Neural Processing Unit", C_PINK, 4)
        soc = RoundedRectangle(width=6.0, height=4.2, corner_radius=0.15)
        soc.set_stroke(C_GREY, 2).set_fill("#0b0c0f", 1)
        cpu = labeled_box("CPU cores", 2.6, 1.5, color=C_BLUE, size=22)
        gpu = labeled_box("GPU", 2.6, 1.5, color=C_YELLOW, size=22)
        npu = labeled_box("NPU", 2.6, 1.5, color=C_PINK, size=30, fill_opacity=0.3)
        isp = labeled_box("camera / media", 2.6, 1.5, color=C_GREY, size=20)
        blocks = VGroup(cpu, gpu, npu, isp).arrange_in_grid(2, 2, buff=0.2)
        blocks.move_to(soc)
        soc_l = T("one laptop / phone chip", size=22, color=C_GREY).next_to(soc, UP, 0.15)
        mem = labeled_box("shared LPDDR5X memory", 6.0, 0.6, color=C_BLUE, size=20)
        mem.next_to(soc, DOWN, buff=0.35)
        link = Line(soc.get_bottom(), mem.get_top(), color=C_BLUE, stroke_width=5)
        chip = VGroup(soc_l, soc, blocks, link, mem).move_to(LEFT * 3.0 + DOWN * 0.45)
        with self.voiceover(
            "The NPU, or Neural Processing Unit, is the AI block inside your phone or laptop "
            "chip. Apple calls it the Neural Engine. Qualcomm, Intel and AMD all have their own."
        ) as vo:
            self.play(FadeIn(head, shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeIn(soc), FadeIn(soc_l), LaggedStart(*[FadeIn(b) for b in blocks],
                                                             lag_ratio=0.2), run_time=1.6)
            self.play(Create(link), FadeIn(mem), run_time=0.8)
            self.play(Indicate(npu, color=C_PINK, scale_factor=1.08), run_time=1.0)

        # low precision bit strips
        def strip(bits, col):
            return VGroup(*[Square(0.2).set_stroke(col, 1).set_fill(col, 0.6)
                            for _ in range(bits)]).arrange(RIGHT, buff=0.03)
        rows = VGroup()
        for bits, col in [(16, C_GREY), (8, C_PINK), (4, C_PINK)]:
            lab = T(f"{bits}-bit", size=22, color=col).set_width(0.8)
            rows.add(VGroup(lab, strip(bits, col)).arrange(RIGHT, buff=0.25))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(RIGHT * 3.4 + UP * 0.9)
        with self.voiceover(
            "It does the same kind of matrix math as a TPU, but tuned for low power, using 8-bit "
            "and 4-bit numbers instead of 16. The NPU in Qualcomm's Snapdragon X Elite does 45 "
            "trillion operations per second, on just a few watts."
        ) as vo:
            self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.2) for r in rows], lag_ratio=0.3),
                      run_time=1.6)
            fewer = T("fewer bits → less energy, less memory", size=22, color=C_PINK)
            fewer.next_to(rows, DOWN, buff=0.25).align_to(rows, LEFT)
            self.play(FadeIn(fewer), run_time=0.6)
            big = T("45 TOPS", size=56, color=C_PINK)
            sub = T("Snapdragon X Elite NPU · INT8 · a few watts", size=20, color=C_GREY)
            g = VGroup(big, sub).arrange(DOWN, buff=0.1).next_to(fewer, DOWN, buff=0.5)
            g.align_to(rows, LEFT)
            self.wait(max(0.1, self.remaining(vo) - 2.2))
            self.play(Write(big), FadeIn(sub), run_time=1.2)
            spec_top = VGroup(rows, fewer, g)

        with self.voiceover(
            "That's what runs face unlock, live captions, photo cleanup and background blur on "
            "calls, without draining your battery or sending your data to the cloud."
        ) as vo:
            uses = VGroup(*[T(u, size=26, color=C_WHITE) for u in
                            ["face unlock", "live captions", "photo cleanup", "background blur"]])
            uses.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
            uses.move_to(RIGHT * 3.4 + DOWN * 0.2)
            self.play(FadeOut(spec_top), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(u, shift=LEFT * 0.2) for u in uses], lag_ratio=0.35),
                      run_time=min(3.0, vo.duration - 1.5))
            local = T("on device · on battery · private", size=22, color=C_PINK)
            local.next_to(uses, DOWN, buff=0.35).align_to(uses, LEFT)
            self.play(FadeIn(local), run_time=0.6)

        with self.voiceover(
            "Yardstick: laptop memory runs at about 135 gigabytes per second, so our 8 gigabyte "
            "model tops out around 17 tokens per second. Small models run on device. Big ones "
            "still go to the data center."
        ) as vo:
            self.play(FadeOut(VGroup(uses, local)), chip.animate.shift(UP * 0.4).scale(0.9),
                      run_time=0.6)
            ys = yardstick(r"135\ \text{GB/s}", r"17\ \text{tokens/s}", color=C_PINK)
            ys.move_to(RIGHT * 3.4 + UP * 0.3)
            self.play(FadeIn(ys, shift=UP * 0.2), run_time=1.0)
            note = VGroup(T("small models: on device", size=24, color=C_PINK),
                          T("big models: data center", size=24, color=C_GREY)).arrange(
                DOWN, aligned_edge=LEFT, buff=0.15).next_to(ys, DOWN, buff=0.5)
            self.wait(1.2)
            self.play(FadeIn(note, shift=UP * 0.1), run_time=0.8)
        self.clear_all(run_time=0.6)
