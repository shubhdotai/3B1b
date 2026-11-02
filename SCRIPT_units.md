# Narration script

## Intro  (00:00)

A single CPU core ticks about four billion times per second. An NVIDIA H100 GPU does about a thousand trillion math operations per second. A Cerebras wafer moves twenty one petabytes of data per second. Each of these is a processing unit, and each exists for a different reason.

Here are nine of them, with real numbers: CPU, GPU, TPU, NPU, LPU, wafer-scale engines, FPGA, ASIC, and DPU.

To compare them, we'll use one yardstick. When an AI model writes text, every new word requires reading every weight of the model from memory. So the speed limit is simple: memory bandwidth, divided by model size.

Our test model: 8 billion parameters, stored at one byte each. That's 8 gigabytes to read for every single token.


## CPU  (00:53)

The CPU: a few dozen big, smart cores. A server chip like AMD's EPYC 9654 has 96 of them: twelve chiplets of eight cores each, running at up to 3.7 gigahertz.

Each core is built to finish one stream of instructions as fast as possible. It predicts which way branches will go, runs instructions out of order, and keeps 384 megabytes of cache close by. That makes it great at messy, unpredictable work: operating systems, databases, game logic, your browser.

For raw math it's limited: about ten teraflops across all 96 cores, roughly a hundred times less than a GPU's matrix units. Its memory is twelve channels of DDR5, about 460 gigabytes per second.

Divide by our 8 gigabyte model, and you get about 57 tokens per second, at best. Usable, but not fast.


## GPU  (01:45)

The GPU: instead of a few smart cores, thousands of simple ones. The H100 has 16,896 CUDA cores, grouped into 132 streaming multiprocessors, plus 528 Tensor Cores built only for matrix math.

Threads run in groups of 32 called warps, all executing the same instruction on different data. That's terrible for branchy code, where half the warp sits idle, but perfect for graphics and neural networks, where you do the same multiply-add millions of times.

The numbers: about 990 teraflops of 16-bit matrix math, 80 gigabytes of high bandwidth memory at 3.35 terabytes per second, and 700 watts.

Yardstick: 3.35 terabytes per second over 8 gigabytes is about 420 tokens per second. Seven times the CPU, and mostly because of memory, not math.


## TPU  (02:39)

The TPU, Google's Tensor Processing Unit. It isn't a general-purpose chip at all. It's built around one structure: the systolic array.

Picture a 128 by 128 grid of multiply-accumulate cells. Weights sit inside the cells. Input numbers pulse in from the left, one step per clock, and partial sums flow down. Every value gets reused across a whole row or column, without ever going back to memory.

That's why it's efficient: almost no energy goes into fetching data. A TPU v5e chip delivers 197 teraflops of 16-bit math, with 16 gigabytes of memory at 819 gigabytes per second.

Yardstick: about 100 tokens per second per chip. But TPUs are meant to be used in pods of up to 256 chips, wired directly to each other.


## NPU  (03:32)

The NPU, or Neural Processing Unit, is the AI block inside your phone or laptop chip. Apple calls it the Neural Engine. Qualcomm, Intel and AMD all have their own.

It does the same kind of matrix math as a TPU, but tuned for low power, using 8-bit and 4-bit numbers instead of 16. The NPU in Qualcomm's Snapdragon X Elite does 45 trillion operations per second, on just a few watts.

That's what runs face unlock, live captions, photo cleanup and background blur on calls, without draining your battery or sending your data to the cloud.

Yardstick: laptop memory runs at about 135 gigabytes per second, so our 8 gigabyte model tops out around 17 tokens per second. Small models run on device. Big ones still go to the data center.


## LPU & wafer-scale  (04:21)

The LPU, Groq's Language Processing Unit, attacks the memory problem head on. It has no external memory at all. Each chip holds 230 megabytes of on-chip SRAM, readable at 80 terabytes per second: about 24 times the H100's memory bandwidth.

The catch: 230 megabytes is tiny. A 70 billion parameter model needs about 300 of these chips, chained together, with a compiler scheduling every data movement ahead of time, down to the clock cycle.

Cerebras takes the idea to the extreme. Instead of cutting a silicon wafer into hundreds of chips, it keeps the whole wafer as one chip: 46,225 square millimeters, 4 trillion transistors, 900,000 cores, and 44 gigabytes of SRAM at 21 petabytes per second.

The payoff is speed. Cerebras has reported around 1,800 tokens per second on Llama 3.1 8B, several times what a single GPU manages.


## FPGA & ASIC  (05:21)

The FPGA, or Field-Programmable Gate Array, is hardware you can rewire. It's a sea of small lookup tables, flip-flops and math blocks, with programmable wiring between them. Load a new configuration file, and the same chip becomes a different circuit.

That gives you custom hardware without building a chip: sub-microsecond latency for high-frequency trading, network packet processing, and prototyping chips before they're manufactured. The cost: clock speeds of a few hundred megahertz, and much harder programming.

The ASIC, or Application-Specific Integrated Circuit, is the opposite: a chip that does exactly one thing, permanently. The TPU is an ASIC. So is a Bitcoin miner. An Antminer S21 computes 200 trillion hashes per second, something no CPU or GPU comes close to per watt.

The trade-off is cost and time. A cutting-edge ASIC can cost tens of millions of dollars and years to design, and if the algorithm changes, the chip is obsolete.


## DPU  (06:21)

Last, the DPU, or Data Processing Unit. In a data center, a lot of CPU time goes to moving data around: networking, storage, encryption. A DPU takes that job over.

NVIDIA's BlueField-3 combines a 400 gigabit per second network interface with 16 Arm cores and hardware engines for encryption and storage, all on one card.

In AI clusters, where thousands of GPUs constantly exchange data, the DPU keeps the network moving, so the CPUs and GPUs can focus on their own work.


## The lineup  (06:54)

So here's the lineup by memory bandwidth, the number that decides how fast text comes out. From a laptop NPU at 135 gigabytes per second, to a Cerebras wafer at 21 petabytes per second. That's a range of over a hundred thousand times.

And by job: the CPU for logic and control. The GPU for parallel math. The TPU and NPU for neural networks, in the data center and on device. The LPU and wafer-scale engines for very fast generation. FPGAs for custom low-latency circuits. ASICs for one job, done perfectly. And DPUs for moving data.

Every one of them is a different answer to the same question: where do you spend your transistors? On smart control, on raw math, or on memory right next to the math.

