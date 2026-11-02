# Narration script

## Intro  (00:00)

When you ask a large language model a question, the answer appears one word at a time, almost like someone is typing it.

Each of those little pieces of text, called tokens, is the output of an enormous computation: billions of multiplications, carried out on a chip called a GPU.

In this video, let's open up that chip: from how the hardware is organized, all the way up to the tricks that make modern chatbots fast.

And along the way we'll run into a surprising fact. For most of the time a GPU spends generating text, the bottleneck is not the math. The arithmetic units sit mostly idle. The real limit is something much more mundane: how quickly you can move numbers out of memory.

To see why, let's start with a more basic question. What even makes a GPU different from the CPU in your laptop?


## 1. CPU vs GPU  (00:48)

A CPU is a brilliant generalist: a handful of very powerful cores, each surrounded by large caches and clever control logic that predicts branches, reorders instructions, and does everything it can to finish a single stream of work as fast as possible.

A GPU makes the opposite bet. It strips each core down to little more than an arithmetic unit, and then packs in thousands of them. Any one of these cores is slow and simple, but together they have enormous throughput.

Think of it as a few brilliant professors versus a stadium full of students who each know how to multiply and add. For a hard, sequential problem, you want the professors. For millions of independent little calculations, the stadium wins by a landslide.

And it just so happens that the core operation of neural networks is exactly that kind of problem: matrix multiplication.

Each entry of the output is a dot product between one row of the first matrix and one column of the second. Crucially, no entry depends on any other. So you can hand each one to a different worker, and compute them all at the same time.

This is the whole reason GPUs, originally built to color in pixels for video games, ended up powering the AI revolution. Shading millions of pixels and multiplying giant matrices turn out to be the same kind of job.


## 2. Inside a GPU  (02:08)

Let's take a concrete example: NVIDIA's H100, one of the workhorse chips for running large language models today.

Most of the chip is this repeating tile, called a Streaming Multiprocessor, or S M. The H100 has 132 of them. Through the middle runs a 50 megabyte L2 cache, shared by all of them. And right next to the chip sit stacks of high bandwidth memory, H B M, holding 80 gigabytes. This is where the model's weights live.

Let's zoom in on one SM. It has four quadrants, each with its own scheduler, a big register file, a few dozen simple arithmetic units, the so-called CUDA cores, and one much more specialized unit: a Tensor Core. Shared across the whole SM is a small, fast scratchpad of memory, a couple hundred kilobytes, that programmers manage directly.

The work given to a GPU is organized in a similar hierarchy. The smallest unit is a thread: one worker. Threads are bundled into groups of thirty two called warps, which all execute the same instruction at the same time, each on its own data. Warps are grouped into thread blocks, each running on a single SM and sharing its scratchpad memory. And the whole job, the grid, can contain thousands of blocks, spread across all the SMs.

The Tensor Cores do almost all the heavy lifting for A I. Instead of multiplying one pair of numbers at a time, a Tensor Core takes in small matrices, multiplies them, and adds the result to an accumulator, all as a single operation.

Add it all up, and an H100 can perform roughly a thousand trillion floating point operations every second, at sixteen bit precision. That's a petaflop, on a single chip.

But here's the catch. Those numbers have to come from somewhere. And the different kinds of memory on the GPU form a hierarchy, with a brutal trade-off between size and speed.

At the top are the registers, tiny but instantaneous. Then the shared memory inside each SM. Then the L2 cache. And at the bottom, the 80 gigabytes of H B M, which can deliver data at about three point three five terabytes per second.

That sounds fast, but compare it to the compute. A thousand teraflops divided by three point three five terabytes per second means that for every byte you pull from H B M, the GPU could do about three hundred operations. Do less work than that per byte, and the arithmetic units just sit there, waiting for data.


## 3. Feeding the beast  (04:37)

This ratio, operations performed per byte moved, is called arithmetic intensity, and it's the single most useful number for thinking about GPU performance.

Take matrix multiplication again. If every output entry naively went back to main memory to fetch its own row and its own column, the same numbers would be fetched over and over, and the intensity would be terrible.

Instead, well-written GPU code uses a technique called tiling. A thread block loads one square tile of each input matrix into the fast shared memory, just once. Then every thread in the block reuses those values many times, accumulating partial results for a whole tile of the output. Then it slides on to the next pair of tiles.

The bigger the tile, the more reuse you get out of every byte. For an n by n tile, you move on the order of n squared numbers, but do on the order of n cubed operations. So the intensity grows with the size of the tile.

A nice way to picture all of this is with what's called a roofline plot. On the horizontal axis, arithmetic intensity. On the vertical axis, the actual throughput you achieve.

At low intensity you're limited by memory bandwidth. Your speed is just bandwidth times intensity: this slanted line. At high intensity you hit the ceiling of how fast the chip can compute. The corner where they meet, around three hundred operations per byte for the H100, is called the ridge point.

Everything to the left is memory-bound. Everything to the right is compute-bound. Keep this picture in mind, because the story of LLM inference is really the story of where on this plot each part of the computation lands.


## 4. What an LLM computes  (06:17)

Quick refresher on what a language model actually computes. If you've seen how transformers work, this will be familiar.

The text is broken into tokens, and each token is turned into a long vector of numbers. These vectors flow through a sequence of layers. In each layer, an attention block lets the vectors exchange information with each other, and a multilayer perceptron block updates each vector on its own.

At the end, the last vector is turned into a probability distribution over every possible next token. One is sampled, appended to the text, and the whole process repeats.

Notice that almost every step here is a matrix multiplication: a big matrix of learned weights, multiplied by the token vectors. The attention projections, the MLP layers, the final unembedding. All weights. All matrix products.

And there are a lot of weights. An open model like Llama 3 with 8 billion parameters, at two bytes each, takes up 16 gigabytes, and frontier models are far larger. For our running example, let's put that 8 billion parameter model on one H100.


## 5. Prefill and decode  (07:26)

Generating a response actually happens in two very different phases.

First comes prefill: reading your prompt, say, a thousand tokens. Since they're all known up front, they can be processed in parallel. Each weight matrix multiplies a big matrix holding all thousand token vectors at once.

That means every weight we load from memory gets reused a thousand times. The arithmetic intensity is high, and prefill lands comfortably on the compute-bound side of the roofline. The GPU is doing what it was built for.

Then comes decode, generating the answer. And here's the problem. Each new token depends on the one before it, so they have to be produced one at a time. Each step multiplies the weight matrices by just a single vector.

To do that, the GPU has to stream every one of those 16 gigabytes of weights out of H B M and through the S M's. And for each weight, a pair of bytes, it does just two operations: one multiply, one add. That's an arithmetic intensity of about one. Way, way down at the left of the roofline.

Let's put numbers on it. Reading 16 gigabytes at 3.35 terabytes per second takes about five milliseconds. The math itself, around 16 billion operations, would take the tensor cores about sixteen microseconds. So during decode, the compute units are idle more than ninety nine percent of the time.

This sets a hard speed limit. No matter how clever the code, one user on this setup can never get more than about two hundred tokens per second. The speed of text generation is fundamentally the speed of memory.


## 6. Batching  (09:06)

So how do companies serve millions of people with such hardware? The key trick is batching.

If a hundred different users are each waiting for their next token, the server can stack their hundred vectors side by side into a matrix. Now each weight is loaded from memory once, but used a hundred times.

Since the time per step was dominated by reading the weights, processing a hundred users costs barely more than processing one. Throughput grows almost linearly with batch size, and the point on the roofline slides to the right, toward the ridge.

In practice, requests arrive and finish at different times, so modern servers use continuous batching: at every step, finished sequences leave, and waiting requests jump into the open slots, keeping the GPU full.

But batching runs into a second memory problem, and to see it, we need to look inside attention.


## 7. The KV cache  (10:00)

Remember that in attention, each token produces a query, a key, and a value. The new token's query is compared against the keys of every previous token, and those comparisons decide how to weight their values.

During decode, the keys and values of earlier tokens never change. So rather than recomputing them every step, we compute them once and store them. This is called the K V cache.

How big is it? For our 8 billion parameter model, each token stores a key and a value, in each of 32 layers, for 8 key-value heads of dimension 128, at two bytes each. That comes out to about 128 kilobytes per token.

That doesn't sound like much, until you multiply it out. A single conversation with eight thousand tokens of context needs about a gigabyte. A batch of sixty four such conversations needs sixty four gigabytes, four times as much as the model weights themselves!

And at every decode step, that entire cache has to be read from memory too. So the K V cache limits how big your batch can be, and it adds more memory traffic: the exact resource we're already short on.

Early serving systems also wasted a lot of this memory, reserving one big contiguous chunk for each request's maximum possible length. v L L M's Paged Attention fixed this with an idea borrowed from operating systems: split the cache into small, fixed size pages that can live anywhere in memory, and keep a table of where each sequence's pages are. Almost nothing is wasted, so many more requests fit in a batch.


## 8. FlashAttention  (11:38)

There's one more place where attention fights against the memory hierarchy, especially during prefill on long prompts.

Computing attention naively means forming the full grid of scores, every query against every key. For a prompt of N tokens, that's an N by N matrix. The straightforward approach writes this whole grid out to H B M, reads it back to apply the softmax, writes it out again, then reads it back once more to multiply by the values.

For long contexts this grid is enormous, and all that back and forth traffic with H B M dominates the run time.

FlashAttention restructures the computation using the same tiling idea from before. Load a block of queries into shared memory. Then stream through the keys and values one block at a time, computing that small patch of scores, and folding it into the output right away.

The tricky part is the softmax, which normally needs to see an entire row before it can normalize. The solution: keep a running maximum and a running sum for each row. Whenever a new block reveals a larger maximum, you simply rescale what you've accumulated so far. The final answer is exactly the same, but the giant N by N matrix never touches H B M at all.

Same math, a fraction of the memory traffic, and often several times faster. It's a beautiful example of a recurring theme: on modern hardware, the cleverest algorithm is often the one that moves the fewest bytes.


## 9. Thinking in bytes  (13:05)

Once you see the world in terms of bytes moved, a lot of the other tricks in modern inference start to make sense.

Quantization stores each weight with fewer bits: say eight, or even four, instead of sixteen. Fewer bytes to read per token means faster decoding, almost in direct proportion.

Speculative decoding uses a small, fast draft model to guess the next several tokens. The big model then checks all of those guesses in a single pass. Since checking several tokens at once is like a tiny prefill, it costs about the same as generating one. Every guess that turns out right is a token you got nearly for free.

And for models too large for one chip, the weights are split across many GPUs, connected by very high bandwidth links, so that each chip only has to stream its own slice.

So next time you watch an answer stream onto your screen, picture what's underneath. For every token, billions of weights flow up out of high bandwidth memory, into thousands of tiny arithmetic units that finish almost instantly, and then wait for more.

The math was never really the hard part. The hard part is feeding it.

