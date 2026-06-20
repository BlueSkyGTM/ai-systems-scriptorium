# Exercise 15 — Voice Agents & Benchmark Literacy

**Goal** — Two small reads, no build: sketch a voice pipeline's latency budget and find where it breaks, then decompose one benchmark card into composition, contamination, and what it does not measure.

**Why** — Voice engineering is governed by a latency budget, and benchmark literacy is what keeps you from quoting a saturated number as if it meant progress. Both are reading skills you need before Module 6, where the voice assistant gets built for real. This exercise builds the read, not the system.

**Steps**

1. **The latency budget.** Create `module4-fleet/voice-latency-budget.md`. Lay out the pipeline VAD → STT → LLM → TTS → transport. Assign a plausible millisecond cost to each hop (estimates are fine — cite a source if you have one) and sum them. Then:

   - State whether your total fits the ~450–600ms end-to-end budget from the lesson.
   - If it breaks, name the hop you'd cut first and how (direct-audio `MultimodalAgent` to drop STT/TTS, a faster model, streaming partial audio earlier).
   - Write one sentence on the trade you'd accept for that cut — fewer milliseconds against what you give up (per-stage control, swappable components, instrumentation).

2. **The benchmark card.** Pick ONE benchmark from lesson 15 (SWE-bench Verified, SWE-bench Pro, GAIA, WebArena, or OSWorld). Add a section to the same file with:

   - **Composition** — what's actually in it (task count, source, how a task is scored).
   - **Contamination** — is there a known leakage or saturation story? (For SWE-bench, yes — name it.)
   - **Does NOT measure** — three capabilities this benchmark is silent on. Be specific (e.g. "OSWorld says nothing about code-diff quality").

3. Verify both parts use a number from the lesson and mark it the way the lesson does — these are claims about composition and contamination, not trivia.

**Done when**

- `voice-latency-budget.md` exists with a per-hop budget that sums to a total, a verdict against the ~450–600ms window, and a named first cut with its trade-off.
- The benchmark section names composition, contamination, and exactly three things the benchmark does not measure.
- At least one benchmark number is quoted with its composition caveat attached (e.g. "59.8% on SWE-bench Verified — but 161/500 tasks are 1–2 line changes").

**Stretch** — Take one benchmark number that has been quoted to you outside this course (a vendor blog, a launch post) and decompose it the same way. Write one sentence on what the headline number hid.
