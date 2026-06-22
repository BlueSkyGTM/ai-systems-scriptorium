# Exercise: Profile Under Load

## Goal

See the memory-bandwidth-bound signature on your own rig: high `mem%` with `sm%` well below 100
while a generation runs.

## Why

You cannot tune what you have not profiled. `sm%` and `mem%` together tell you whether you are
constrained by compute or by memory bandwidth, and that answer determines which levers are worth
pulling. Looking at the numbers once, on a real workload, makes everything in the next lesson
concrete.

## Steps

1. Open two terminals side by side.

2. In the first terminal, start the streaming metric watcher:

   ```bash
   nvidia-smi dmon -s um
   ```

   Leave it running. A new row prints every second.

3. In the second terminal, start a long generation. Any method works; for example, using ollama:

   ```bash
   ollama run llama3.2 "Write a detailed explanation of how transformer attention works, at least 500 words."
   ```

   Or, if you have `bench.py` from Module 5, point it at a long prompt. The key is that the
   generation runs for at least 20 to 30 seconds so you get a stable reading.

4. While the generation runs, note the values in the `sm%` and `mem%` columns. Ignore the first
   two or three rows (model load spikes are not the same as generation steady-state). Read the
   steady-state values during active generation.

5. Also note the VRAM usage shown in a standard `nvidia-smi` output (or check `ollama ps`).
   Record how much headroom you have between current usage and the card's total VRAM.

6. Write down:
   - Peak `sm%` during generation (representative value, not the spike at load)
   - Peak `mem%` during generation
   - VRAM used vs. total (for example, `12.4 GB / 16 GB`)
   - One sentence: is your workload memory-bandwidth-bound, compute-bound, or unclear?

## Note: No Rig Available

If you do not have a GPU rig to run this on, read the representative `dmon` output in the lesson
and answer the following from it:

- What does the signature look like in numbers?
- Why is `sm%` not pegged at 100 even though the GPU is working?
- What would change if you ran a training step (large batch) instead of a single token generation?

Write your answers in a text file or in a notebook cell. The goal is the same: understanding what
the numbers mean before you try to move them.

## Done When

You can state clearly, from the `sm%` and `mem%` split you observed (or read), whether your
token-generation workload is memory-bandwidth-bound, and you know which number was the ceiling.

## Stretch

Run the same generation again, but this time use a much longer context: paste in a long document
and ask a question about it, or set a high `num_ctx` in Ollama. Watch the VRAM-usage figure in
`nvidia-smi` as the KV cache grows. Note whether `mem%` changes and whether VRAM headroom
narrows. This connects to the KV-cache tuning lever in the next lesson.
