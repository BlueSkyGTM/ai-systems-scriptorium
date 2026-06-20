# Exercise: Fine-Tuning, in Practice and in Proportion

## Goal

A decision exercise — no GPU, no training. Given a written scenario, argue fine-tune vs RAG vs prompt against cost, data, latency, and reversibility, defend the call in writing, and if the answer is fine-tune, sketch and justify a minimal `LoraConfig` by reasoning about it, not running it.

## Why

The skill an interview probes is not running a training job — it is knowing when *not* to, and speaking precisely about the case where you would.

## Steps

1. In `module5-serving/`, create a `decisions/` folder. This exercise produces written artifacts and one config sketch — no model is loaded or trained.
2. Pick (or write) three scenarios with genuinely different right answers. Suggested set:
   - **A.** "The assistant doesn't know our internal product catalog, which changes weekly." (knowledge that drifts)
   - **B.** "Outputs must always be valid JSON in our exact schema, and prompting gets it right only ~90% of the time." (durable form)
   - **C.** "Responses should sound more formal." (tone — try the cheapest lever first)
3. For each scenario, write `decisions/<scenario>.md` answering, in order:
   - **The lever:** prompt, retrieve, or fine-tune — and the one-line reason.
   - **Cost / data / latency / reversibility:** a sentence each on what the chosen lever costs on each axis versus the rejected ones.
   - **The measure-first plan:** what eval baseline you'd set with prompting, how far you'd expect retrieval to move it, and the number that would have to remain unsolved before fine-tuning earns its cost.
   - **The trap:** name the wrong answer this scenario tempts you toward and why it's wrong (e.g. fine-tuning to add knowledge that retrieval should supply).
4. For the one scenario where fine-tuning is genuinely the right call (B), add `decisions/lora_sketch.py`: a `LoraConfig` written out with every parameter (`r`, `lora_alpha`, `target_modules`, `lora_dropout`, `bias`, `task_type`) and a comment on each line justifying the value. Do **not** call `get_peft_model` or load a model — this is a reasoned sketch.
5. In a comment block at the bottom of `lora_sketch.py`, note one line: what would change if you had to fit this on a single consumer GPU (the QLoRA move — 4-bit base via `BitsAndBytesConfig`, adapters on top).

## Done when

- Three `decisions/<scenario>.md` files exist, each naming a lever, costing it on all four axes, giving a measure-first plan, and naming the trap.
- The three scenarios do not all reach the same answer (at least one prompt, one retrieve, one fine-tune).
- `decisions/lora_sketch.py` contains a complete `LoraConfig` with a per-parameter justification comment and the one-line QLoRA note — and imports nothing heavy, runs nothing, trains nothing.
- Nothing in the exercise requires a GPU, an API key, or a downloaded model.

## Stretch

Add `decisions/REBUTTAL.md`: take the strongest counter-argument to your scenario-B fine-tune call (someone insisting a stricter prompt plus a JSON-schema validator and a retry would beat fine-tuning) and either defend the fine-tune or concede it — with the eval number that would settle the argument.
