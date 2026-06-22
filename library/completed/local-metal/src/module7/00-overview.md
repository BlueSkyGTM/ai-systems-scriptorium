# Module 7: Perf and Tuning

The rig works. It serves a model, routes between local and cloud, and answers to Claude Code. Every
number it produces so far, though, came from stock settings: whatever Ollama defaulted to the day you
installed it. Those defaults are conservative, and they are the starting line, not the finish. This
module is where you tune.

Tuning a single consumer GPU is not the same job as tuning a datacenter. You have one card, a fixed
memory budget, and a handful of levers that actually move the needle. The discipline that matters is
not knowing a hundred flags; it is the loop a production engineer runs without thinking: measure,
change one thing, measure again, and keep the change only if the number improved. This module makes
that loop explicit and gives you the tools to run it.

You start by profiling, because tuning blind is guessing. Token generation is bound by memory
bandwidth, not raw compute, so the signature you learn to read is a GPU that is busy moving weights,
not one pegged at full math utilization. Then you meet the levers worth pulling on this card: flash
attention, KV-cache quantization, request parallelism, and context sizing, each with the tradeoff it
actually carries rather than the speedup a forum post promised.

The measurement that ties it together is throughput under load. The single-stream tokens per second
you recorded in Module 4 is the wrong metric for a server that answers more than one request at a time.
You will build `loadbench.py` to fire concurrent generations and report aggregate throughput and the
slowest request, the numbers that tell you whether the rig holds up when you actually lean on it.

You leave this module, and the book, with a seventh file in the portfolio repository: `TUNING.md`, a
before-and-after that shows the baseline from Module 4, the result after tuning, and exactly which
levers moved which number. Seven modules ago this was a parts list. Now it is a documented, routed,
wired, and tuned inference host, with seven files that prove every claim. That before-and-after is the
last word the book asks you to write, and the first thing a reviewer should read.
