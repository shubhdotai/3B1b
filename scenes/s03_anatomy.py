import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import *  # noqa: E402,F403


def thread_glyph(color=C_YELLOW, h=0.55):
    """A thread drawn as a little wavy strand with a head."""
    wave = FunctionGraph(lambda t: 0.06 * np.sin(t * 18), x_range=[0, h], color=color,
                         stroke_width=2.5).rotate(-PI / 2)
    head = Dot(radius=0.05, color=color).move_to(wave.get_top())
    return VGroup(wave, head)


class Anatomy(VoiceScene):
    def construct(self):
        self.chapter_card(2, "Inside a GPU")
        frame = self.camera.frame
        frame.save_state()

        chip = gpu_chip(width=7.0, height=4.6)
        chip.shift(DOWN * 0.2)
        title = T("NVIDIA H100", size=44).to_edge(UP, buff=0.35)

        with self.voiceover(
            "Let's take a concrete example: NVIDIA's H100, one of the workhorse chips "
            "for running large language models today."
        ) as vo:
            self.play(Write(title), run_time=1.0)
            self.play(FadeIn(chip.die), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(g) for g in chip.gpcs], lag_ratio=0.15),
                      FadeIn(chip.l2), FadeIn(chip.l2_label), run_time=1.6)
            self.play(LaggedStart(*[FadeIn(h, shift=(h.get_center() - chip.die.get_center())
                                           * 0.1) for h in chip.hbm], lag_ratio=0.1),
                      run_time=1.2)

        with self.voiceover(
            "Most of the chip is this repeating tile, called a Streaming Multiprocessor, or "
            "S M. The H100 has 132 of them. Through the middle runs a 50 megabyte L2 cache, "
            "shared by all of them. And right next to the chip sit stacks of high bandwidth "
            "memory, H B M, holding 80 gigabytes. This is where the model's weights live."
        ) as vo:
            sm0 = chip.sms[0]
            self.play(Indicate(sm0, color=C_WHITE, scale_factor=1.6), run_time=1.2)
            self.play(LaggedStart(*[sm.animate.set_fill(C_YELLOW, 0.8) for sm in chip.sms],
                                  lag_ratio=0.01), run_time=2.0)
            sm_lab = T("132 Streaming Multiprocessors", size=30, color=C_YELLOW)
            sm_lab.next_to(chip, DOWN, buff=0.3)
            self.play(Write(sm_lab), chip.sms.animate.set_fill(C_YELLOW, 0.28), run_time=1.4)
            self.wait(1.4)
            self.play(chip.l2.animate.set_fill(C_BLUE, 0.6), Indicate(chip.l2_label),
                      run_time=1.4)
            self.play(chip.l2.animate.set_fill(C_BLUE, 0.25), run_time=0.6)
            self.wait(1.2)
            hbm_l = hbm_labels(chip, size=24)
            hbm_lab = T("HBM · 80 GB", size=30, color=C_BLUE).next_to(chip, DOWN, buff=0.3)
            self.play(chip.hbm.animate.set_fill(C_BLUE, 0.75), FadeIn(hbm_l),
                      ReplacementTransform(sm_lab, hbm_lab), run_time=1.4)
            w = T("model weights live here", size=26, color=C_GOLD)
            w.next_to(hbm_lab, DOWN, buff=0.15)
            self.play(FadeIn(w, shift=UP * 0.1), run_time=0.8)

        # --- Zoom into one SM -----------------------------------------------
        target = chip.sms[5]
        sm = sm_detail()
        with self.voiceover(
            "Let's zoom in on one SM. It has four quadrants, each with its own scheduler, "
            "a big register file, a few dozen simple arithmetic units, the so-called CUDA "
            "cores, and one much more specialized unit: a Tensor Core. Shared across the "
            "whole SM is a small, fast scratchpad of memory, a couple hundred kilobytes, "
            "that programmers manage directly."
        ) as vo:
            self.play(FadeOut(VGroup(hbm_lab, w, hbm_l, title)), run_time=0.5)
            zoom_w = target.width * 1.5
            self.play(frame.animate.set(width=zoom_w).move_to(target), run_time=2.0)
            k = zoom_w / config.frame_width
            sm.scale(k).move_to(target)
            self.play(FadeIn(sm), run_time=0.8)
            self.drop(chip)
            # reset camera and blow the SM up identically (no visible jump)
            c = frame.get_center().copy()
            frame.restore()
            sm.shift(-c).scale(1 / k, about_point=ORIGIN)
            self.wait(0.3)
            self.play(LaggedStart(*[Indicate(q.frame, color=C_WHITE, scale_factor=1.03)
                                    for q in sm.quads], lag_ratio=0.25), run_time=1.6)
            q0 = sm.quads[0]
            for part, col in [(q0.sched, C_PURPLE), (q0.regs, C_TEAL)]:
                self.play(Indicate(part, color=col, scale_factor=1.08), run_time=0.9)
            self.play(q0.cores.animate.set_fill(C_YELLOW, 0.95), run_time=0.6)
            cuda = T("CUDA cores", size=26, color=C_YELLOW)
            cuda.set_stroke(BLACK, 5, background=True)
            cuda.next_to(q0.cores, DOWN, buff=0.08)
            self.play(FadeIn(cuda), q0.cores.animate.set_fill(C_YELLOW, 0.35), run_time=0.8)
            self.play(Indicate(q0.tensor, color=C_ORANGE, scale_factor=1.12), run_time=1.0)
            self.play(Indicate(sm.smem, color=C_TEAL, scale_factor=1.04), run_time=1.4)

        # --- Threads, warps, blocks, grids -----------------------------------
        with self.voiceover(
            "The work given to a GPU is organized in a similar hierarchy. The smallest "
            "unit is a thread: one worker. Threads are bundled into groups of thirty two "
            "called warps, which all execute the same instruction at the same time, each "
            "on its own data. Warps are grouped into thread blocks, each running on a "
            "single SM and sharing its scratchpad memory. And the whole job, the grid, can "
            "contain thousands of blocks, spread across all the SMs."
        ) as vo:
            self.play(FadeOut(VGroup(sm, cuda)), run_time=0.6)
            # thread
            th = thread_glyph().scale(1.6).move_to(LEFT * 5.2 + UP * 1.0)
            th_l = T("Thread", size=30, color=C_YELLOW).next_to(th, DOWN, buff=0.3)
            self.play(Create(th[0]), FadeIn(th[1]), Write(th_l), run_time=1.6)
            self.wait(0.8)
            # warp
            warp = VGroup(*[thread_glyph() for _ in range(32)]).arrange(RIGHT, buff=0.06)
            warp.move_to(RIGHT * 1.2 + UP * 1.0)
            warp_box = SurroundingRectangle(warp, color=C_ORANGE, buff=0.12,
                                            corner_radius=0.08)
            warp_l = T("Warp = 32 threads", size=30, color=C_ORANGE).next_to(
                warp_box, DOWN, buff=0.25)
            instr = Mono("FMA  r1, r2, r3", size=24, color=C_WHITE).next_to(warp_box, UP,
                                                                           buff=0.25)
            self.play(LaggedStart(*[TransformFromCopy(th, t) for t in warp],
                                  lag_ratio=0.02), run_time=1.6)
            self.play(Create(warp_box), Write(warp_l), run_time=1.0)
            self.wait(1.2)
            self.play(FadeIn(instr, shift=DOWN * 0.2), run_time=0.6)
            for _ in range(2):
                self.play(*[t.animate.shift(DOWN * 0.12) for t in warp], run_time=0.3)
                self.play(*[t.animate.shift(UP * 0.12) for t in warp], run_time=0.3)
            self.wait(1.0)
            # block
            warp_group = VGroup(warp, warp_box)
            self.play(FadeOut(VGroup(th, th_l, instr, warp_l)),
                      warp_group.animate.scale(0.45).move_to(LEFT * 4.2 + UP * 1.6),
                      run_time=1.0)
            block = VGroup(warp_group, *[warp_group.copy() for _ in range(3)])
            block.arrange(DOWN, buff=0.12).move_to(LEFT * 4.2 + UP * 0.6)
            block_box = SurroundingRectangle(block, color=C_TEAL, buff=0.15,
                                             corner_radius=0.1)
            block_l = T("Thread block", size=28, color=C_TEAL).next_to(block_box, DOWN,
                                                                       buff=0.2)
            on_sm = T("runs on one SM,\nshares its scratchpad", size=22, color=C_GREY)
            on_sm.next_to(block_l, DOWN, buff=0.12)
            self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.2) for b in block[1:]],
                                  lag_ratio=0.2), Create(block_box), Write(block_l),
                      run_time=1.6)
            self.play(FadeIn(on_sm), run_time=0.6)
            self.wait(1.8)
            # grid of blocks onto the chip
            small_chip = gpu_chip(width=5.0, height=3.3, show_labels=False)
            small_chip.move_to(RIGHT * 2.9 + DOWN * 0.3)
            grid_l = T("Grid: thousands of blocks across all SMs", size=28, color=C_WHITE)
            grid_l.next_to(small_chip, UP, buff=0.4)
            self.play(FadeIn(small_chip), Write(grid_l), run_time=1.2)
            blk_icon = VGroup(block, block_box)
            copies = VGroup()
            anims = []
            for i, s in enumerate(small_chip.sms[::2]):
                cpy = Square(0.14).set_stroke(C_TEAL, 1).set_fill(C_TEAL, 0.9)
                cpy.move_to(blk_icon)
                copies.add(cpy)
                anims.append(cpy.animate.move_to(s))
            self.play(LaggedStart(*anims, lag_ratio=0.01),
                      run_time=max(1.0, self.remaining(vo) - 0.5))

        # --- Tensor cores --------------------------------------------------
        with self.voiceover(
            "The Tensor Cores do almost all the heavy lifting for A I. Instead of "
            "multiplying one pair of numbers at a time, a Tensor Core takes in small "
            "matrices, multiplies them, and adds the result to an accumulator, all as a "
            "single operation."
        ) as vo:
            self.clear_all(run_time=0.6)
            rng = np.random.default_rng(5)
            gA = cell_grid(4, 4, 0.42, C_BLUE, rng.uniform(0.2, 0.9, (4, 4)))
            gB = cell_grid(4, 4, 0.42, C_PINK, rng.uniform(0.2, 0.9, (4, 4)))
            gC = cell_grid(4, 4, 0.42, C_GREEN, rng.uniform(0.2, 0.9, (4, 4)))
            gD = cell_grid(4, 4, 0.42, C_YELLOW, np.zeros((4, 4)), min_opacity=0.05)
            eq = VGroup(gD, M("=", 44), gA, M(r"\times", 44), gB, M("+", 44), gC)
            eq.arrange(RIGHT, buff=0.3).shift(DOWN * 1.6)
            labs = VGroup(*[M(s, 36, c).next_to(g, DOWN, buff=0.2) for s, c, g in
                            [("D", C_YELLOW, gD), ("A", C_BLUE, gA), ("B", C_PINK, gB),
                             ("C", C_GREEN, gC)]])
            tc = labeled_box("Tensor Core", 3.6, 1.5, color=C_ORANGE, size=34,
                             fill_opacity=0.25).shift(UP * 1.6)
            scalar = VGroup(T("CUDA core:", size=26, color=C_GREY),
                            M(r"d = a \times b + c", 34, C_YELLOW)).arrange(RIGHT)
            scalar.to_corner(UL, buff=0.5)
            self.play(FadeIn(scalar), run_time=0.8)
            self.play(FadeIn(tc), run_time=0.8)
            self.play(FadeIn(VGroup(gA, gB, gC, eq[1], eq[3], eq[5], gD)),
                      FadeIn(labs), run_time=1.0)
            # inputs fly into the tensor core
            ins = VGroup(gA.copy(), gB.copy(), gC.copy())
            self.play(*[m.animate.scale(0.4).move_to(tc) for m in ins], run_time=1.2)
            self.play(FadeOut(ins), Flash(tc, color=C_ORANGE, line_length=0.4,
                                          flash_radius=1.9), run_time=0.6)
            outv = rng.uniform(0.4, 1.0, (4, 4))
            out = gD.copy()
            for r in range(4):
                for c in range(4):
                    out.cells[r][c].set_fill(C_YELLOW, outv[r, c])
            out.move_to(tc).scale(0.4)
            self.play(Transform(out, gD.copy().set_fill(C_YELLOW, 0.8)), run_time=0.9)
            self.drop(out)
            for r in range(4):
                for c in range(4):
                    gD.cells[r][c].set_fill(C_YELLOW, outv[r, c])
            one_op = T("one instruction", size=30, color=C_ORANGE).next_to(tc, RIGHT,
                                                                          buff=0.4)
            self.play(Write(one_op), run_time=0.8)

        with self.voiceover(
            "Add it all up, and an H100 can perform roughly a thousand trillion floating "
            "point operations every second, at sixteen bit precision. That's a petaflop, "
            "on a single chip."
        ) as vo:
            self.clear_all(run_time=0.6)
            big = T("≈ 1,000 TFLOP/s", size=80, color=C_YELLOW)
            sub = T("dense 16-bit (BF16) matrix math", size=30, color=C_GREY)
            sub.next_to(big, DOWN, buff=0.4)
            self.play(Write(big), run_time=1.6)
            self.play(FadeIn(sub), run_time=0.8)
            pf = T("= 10¹⁵ operations per second", size=40, color=C_WHITE)
            pf.next_to(sub, DOWN, buff=0.5)
            self.play(Write(pf), run_time=1.4)
            compute_card = VGroup(big, sub, pf)

        # --- Memory hierarchy pyramid -------------------------------------
        with self.voiceover(
            "But here's the catch. Those numbers have to come from somewhere. And the "
            "different kinds of memory on the GPU form a hierarchy, with a brutal "
            "trade-off between size and speed."
        ) as vo:
            self.play(compute_card.animate.scale(0.45).to_corner(UR, buff=0.4),
                      run_time=1.0)
            levels = [
                ("Registers", "256 KB per SM", COL_SRAM),
                ("Shared memory / L1", "256 KB per SM", COL_SRAM),
                ("L2 cache", "50 MB", C_BLUE),
                ("HBM", "80 GB  ·  3.35 TB/s", C_BLUE_D),
            ]
            pyr = VGroup()
            top_y, step = 2.2, 1.15
            for i, (name, size, col) in enumerate(levels):
                w_top, w_bot = 1.2 + 1.9 * i, 1.2 + 1.9 * (i + 1)
                y0 = top_y - i * step
                trap = Polygon([-w_top / 2, y0, 0], [w_top / 2, y0, 0],
                               [w_bot / 2, y0 - step + 0.08, 0],
                               [-w_bot / 2, y0 - step + 0.08, 0])
                trap.set_stroke(col, 2).set_fill(col, 0.35 if i < 3 else 0.55)
                lab = T(name, size=26).move_to(trap)
                sz = T(size, size=24, color=col if i < 3 else C_BLUE).next_to(
                    trap, RIGHT, buff=0.3)
                pyr.add(VGroup(trap, lab, sz))
            pyr.shift(LEFT * 1.0 + DOWN * 0.3)
            fast = Arrow(pyr.get_corner(DL) + LEFT * 0.5, pyr.get_corner(UL) + LEFT * 0.5,
                         color=C_TEAL, buff=0)
            fast_l = T("faster", size=24, color=C_TEAL).next_to(fast.get_end(), UP,
                                                                buff=0.1)
            big_l = T("bigger", size=24, color=C_BLUE).next_to(pyr, DOWN, buff=0.2)
            self.play(FadeIn(fast), FadeIn(fast_l), FadeIn(big_l), run_time=1.0)
            self.play(FadeIn(pyr[0][0]), FadeIn(pyr[0][1]), run_time=0.6)

        with self.voiceover(
            "At the top are the registers, tiny but instantaneous. Then the shared memory "
            "inside each SM. Then the L2 cache. And at the bottom, the 80 gigabytes of "
            "H B M, which can deliver data at about three point three five terabytes per "
            "second."
        ) as vo:
            self.play(FadeIn(pyr[0][2], shift=LEFT * 0.2), run_time=0.8)
            self.wait(0.6)
            for lvl in pyr[1:]:
                self.play(FadeIn(lvl, shift=UP * 0.15), run_time=1.0)
                self.wait(0.9)
            self.play(Indicate(pyr[3][2], color=C_BLUE, scale_factor=1.15), run_time=1.0)

        # --- The 300 FLOPs per byte ratio --------------------------------
        with self.voiceover(
            "That sounds fast, but compare it to the compute. A thousand teraflops divided "
            "by three point three five terabytes per second means that for every byte you "
            "pull from H B M, the GPU could do about three hundred operations. Do less work "
            "than that per byte, and the arithmetic units just sit there, waiting for data."
        ) as vo:
            self.play(FadeOut(VGroup(pyr, fast, fast_l, big_l, compute_card)), run_time=0.8)
            ratio = M(r"\frac{1{,}000 \text{ TFLOP/s}}{3.35 \text{ TB/s}}"
                      r"\;\approx\; 300 \ \frac{\text{FLOPs}}{\text{byte}}", 52)
            ratio[0][0:11].set_color(C_YELLOW)
            ratio[0][11:19].set_color(C_BLUE)
            ratio.to_edge(UP, buff=0.8)
            self.play(Write(ratio), run_time=2.4)
            self.wait(1.4)
            byte = Square(0.5).set_stroke(C_BLUE, 2).set_fill(C_BLUE, 0.7)
            byte_l = T("1 byte", size=24, color=C_BLUE).next_to(byte, DOWN, buff=0.15)
            bgrp = VGroup(byte, byte_l).move_to(LEFT * 5 + DOWN * 1.2)
            ops = VGroup(*[Dot(radius=0.05, color=C_YELLOW) for _ in range(300)])
            ops.arrange_in_grid(rows=10, cols=30, buff=0.1).move_to(RIGHT * 1.3 + DOWN * 1.2)
            ops_l = T("≈ 300 operations", size=26, color=C_YELLOW).next_to(ops, DOWN,
                                                                          buff=0.25)
            self.play(FadeIn(bgrp, shift=RIGHT), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(o, scale=2) for o in ops], lag_ratio=0.004),
                      Write(ops_l), run_time=2.0)
            self.wait(1.0)
            # starving: only a few ops used, rest idle
            self.play(ops[12:].animate.set_color(C_GREY_D), run_time=1.2)
            idle = T("waiting...", size=30, color=C_GREY).next_to(ops, UP, buff=0.25)
            self.play(FadeIn(idle), run_time=0.8)
        self.clear_all()
