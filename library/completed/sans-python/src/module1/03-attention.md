# Attention

The encoder-decoder worked — until the sequences got long. Fixed-state seq2seq held 89% accuracy at length 5 and collapsed to near-chance at length 80. The single bottleneck vector could not carry a full sentence. Attention is the fix that made transformers possible.

The problem with fixed-state seq2seq is structural: one vector must summarize the entire source sequence, then the decoder must reconstruct every target token from that single summary. Short sequences fit; long ones don't. The information just doesn't fit in the bottle.

Attention breaks the bottleneck by keeping every encoder hidden state. Instead of collapsing the source into one vector, the decoder gets to look at all of them. At each decoding step, it computes a weighted sum — a context vector — across the encoder states. The weights say which source positions matter right now for this output token. Early tokens weight the beginning of the source; later tokens weight the end. The network learns the alignment.

Bahdanau (2014) introduced the additive form: score the alignment between a decoder state and an encoder state with a small feed-forward network, run softmax over the scores to get weights, sum. Luong (2015) simplified it to a dot product — the multiplicative form — faster to compute, comparable quality. One subtle difference: Bahdanau computes scores from the previous decoder state ($s_{t-1}$) before generating the current hidden state; Luong uses the current one ($s_t$) after. That sequencing difference changes what information is available when scores are computed, and it bites people who mix the two implementations.

The transformer did not invent attention. It took attention and made it the architecture: parallel heads, no recurrence, positional encoding to restore order, scaled dot-product to prevent softmax saturation. "Attention plus engineering" is a fair summary of *Attention Is All You Need* (Vaswani et al., 2017). Every frontier LLM you call today is a descendant of that design.

The pre-attention half — seq2seq, RNNs, CNNs for text — is in the [Antilibrary](../antilibrary.md). You don't need it to reason about what LLM APIs can and can't do.

Knowing that attention is a learned, position-weighted sum over all input tokens explains why context windows exist, why prompt position affects recall, and why long-context limits are a real engineering constraint — not marketing numbers to ignore.

## Core Concepts

- Fixed-state seq2seq degrades sharply with sequence length; attention fixes this by computing a per-step weighted sum over all encoder states instead of compressing to one vector.
- Bahdanau (additive) and Luong (multiplicative) attention differ in scoring function and which decoder state feeds the score — $s_{t-1}$ vs $s_t$ — a sequencing detail that causes silent bugs when implementations are mixed.
- The transformer is attention applied in parallel across multiple heads, without recurrence — not a new idea, but a new architecture built entirely around an existing one.
- Context-window limits, prompt-position sensitivity, and long-context degradation are all downstream consequences of attention's design, not implementation accidents.

<div class="claude-handoff" data-exercise="exercises/module1/03-attention/">

**Try It in Claude Code** — probe a live LLM API to see attention-driven position effects: place the same fact at the start, middle, and end of a long prompt and measure retrieval accuracy across positions.

Open the repo and pick up from this lesson.

</div>
