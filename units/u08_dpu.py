import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import *  # noqa: E402,F403


class DPU(VoiceScene):
    def construct(self):
        head = unit_header("DPU", "Data Processing Unit", C_TEAL, 9)
        net = labeled_box("network", 1.8, 4.0, color=C_GREY, size=22, fill_opacity=0.1)
        net.move_to(LEFT * 5.6 + DOWN * 0.4)
        cpu = labeled_box("CPU", 2.2, 1.3, color=C_BLUE, size=28)
        gpus = VGroup(*[labeled_box("GPU", 1.0, 0.8, color=C_YELLOW, size=20) for _ in range(4)])
        gpus.arrange_in_grid(2, 2, buff=0.15)
        right = VGroup(cpu, gpus).arrange(DOWN, buff=0.5).move_to(RIGHT * 3.6 + DOWN * 0.4)
        load = VGroup(T("CPU time on data chores", size=20, color=C_GREY))
        bar_bg = Rectangle(width=2.2, height=0.25).set_stroke(C_GREY, 1).set_fill(opacity=0)
        bar = Rectangle(width=0.08, height=0.25).set_stroke(width=0).set_fill(C_RED, 0.85)
        bar.align_to(bar_bg, LEFT)
        meter = VGroup(load, VGroup(bar_bg, bar)).arrange(DOWN, buff=0.08).next_to(cpu, UP, 0.2)

        def packets(n, start, end, color=C_TEAL, rt=2.0):
            ds = VGroup(*[Dot(radius=0.07, color=color) for _ in range(n)])
            return ds, flow_animation(ds, start, end, run_time=rt, lag=0.12)

        with self.voiceover(
            "Last, the DPU, or Data Processing Unit. In a data center, a lot of CPU time goes to "
            "moving data around: networking, storage, encryption. A DPU takes that job over."
        ) as vo:
            self.play(FadeIn(head, shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeIn(net), FadeIn(right), FadeIn(meter[0]), FadeIn(bar_bg), run_time=1.0)
            ds, anim = packets(10, net.get_right(), cpu.get_left(), rt=2.0)
            self.add(bar)
            self.play(anim, bar.animate.stretch_to_fit_width(2.2 * 0.35).align_to(bar_bg, LEFT),
                      run_time=2.0)
            self.drop(ds)
            ds, anim = packets(10, net.get_right(), cpu.get_left(), rt=1.6)
            busy = T("busy with data chores", size=20, color=C_RED).next_to(cpu, LEFT, 0.25)
            self.play(anim, bar.animate.stretch_to_fit_width(2.2 * 0.7).align_to(bar_bg, LEFT),
                      FadeIn(busy), run_time=1.6)
            self.drop(ds)
            dpu = labeled_box("DPU", 1.6, 2.4, color=C_TEAL, size=32, fill_opacity=0.25)
            dpu.move_to(LEFT * 1.7 + DOWN * 0.4)
            self.wait(max(0.1, self.remaining(vo) - 2.2))
            self.play(FadeIn(dpu, scale=0.8), FadeOut(busy),
                      bar.animate.stretch_to_fit_width(0.08).align_to(bar_bg, LEFT), run_time=1.2)
            # packets now go through the DPU straight to GPUs
            anims, drops = [], []
            for g in gpus:
                d1, a1 = packets(4, net.get_right(), dpu.get_left(), rt=0.8)
                drops.append(d1)
                anims.append(a1)
            self.play(*anims, run_time=0.8)
            self.drop(*drops)

        board = spec_board([
            ("400 Gb/s", "networking (NVIDIA BlueField-3)", C_TEAL),
            ("16 Arm cores", "run the data-center plumbing", C_TEAL),
            ("hardware engines", "encryption · storage · compression", C_TEAL),
        ], value_size=34, buff=0.26)
        with self.voiceover(
            "NVIDIA's BlueField-3 combines a 400 gigabit per second network interface with 16 "
            "Arm cores and hardware engines for encryption and storage, all on one card."
        ) as vo:
            self.play(VGroup(net, dpu, right, meter, bar).animate.scale(0.6).to_edge(LEFT, buff=0.5)
                      .shift(DOWN * 0.2), run_time=0.8)
            board.move_to(RIGHT * 4.0 + DOWN * 0.3)
            reveal_specs(self, board, run_time=min(3.5, vo.duration - 1.2))

        with self.voiceover(
            "In AI clusters, where thousands of GPUs constantly exchange data, the DPU keeps the "
            "network moving, so the CPUs and GPUs can focus on their own work."
        ) as vo:
            flows, drops = [], []
            for g in gpus:
                d, a = packets(5, dpu.get_right(), g.get_left(), color=C_TEAL, rt=1.4)
                drops.append(d)
                flows.append(a)
            d0, a0 = packets(6, net.get_right(), dpu.get_left(), rt=1.4)
            self.play(a0, *flows, run_time=1.6)
            self.drop(d0, *drops)
            free = T("CPU free for real work", size=22, color=C_BLUE).next_to(meter, UP, 0.15)
            self.play(FadeIn(free), Indicate(cpu, color=C_BLUE, scale_factor=1.05), run_time=1.0)
        self.clear_all(run_time=0.6)
