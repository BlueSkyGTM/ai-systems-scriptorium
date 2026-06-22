# Narrating the Screen

Silence is the failure mode nobody warns you about. You can write correct code, return the right
answer, and still score below the candidate who stumbled through a messier solution, because that
candidate gave the interviewer something to evaluate: a process.

The technical screen is not an answer key. It is an observation of how you think. The interviewer is
watching whether you treat an underspecified prompt as something to clarify, whether you state your
approach before you commit to it, and whether you keep talking when things get hard instead of going
quiet and guessing. The code is the residue. The narration is the signal.

## What the Interviewer Is Collecting

Before the first line of code appears, the interviewer is already forming a picture. They want
evidence of four things: that you decompose a vague prompt before building against it, that you
choose an approach consciously instead of reflexively, that you explain your decisions as you make
them, and that you test your own work. A candidate who silently produces a correct solution in ten
minutes hands the interviewer a black box. A candidate who narrates a slightly rougher solution gives
the interviewer ten minutes of process signal.

That signal is what they write down after you leave.

## The Four Pitfalls

There are four ways a screen goes quiet without the candidate noticing.

The first is **monologuing without check-ins.** You talk continuously but never pause to ask "does
that make sense?" or "is that the direction you had in mind?" The interviewer cannot interrupt the
narration to redirect you, and you spend fifteen minutes in the wrong corner.

The second is **not leading with structure.** You dive into code before stating what you are going to
build. The interviewer cannot follow the implementation because they do not know the plan. Lead with
the shape; code the shape.

The third is **jargon without explanation.** You say "CRAG gate" or "cosine floor" without a sentence
of grounding. The interviewer does not know whether you understand the concept or are borrowing the
label.

The fourth is **defending a wrong answer when the interviewer hints.** An interviewer who says
"interesting, what happens if the list is empty?" is not making conversation. They are pointing at
a gap. The candidate who says "oh, good point, let me revise" scores higher than the one who
explains why the gap is not really a gap.

These four pitfalls are the mechanical failures of a weak screen. The rest of this lesson builds the
habits that prevent them.

## Clarify Before You Code

Every screen prompt is underspecified. That is not an accident; it is part of the test. The
interviewer wants to see whether you treat an ambiguous brief as a contract to negotiate or as an
instruction to execute. Candidates who negotiate always outperform candidates who execute, because
negotiation surfaces assumptions before they turn into bugs.

The clarifying questions are not stalling. They are the first visible sign that you think like an
engineer.

Ask about the inputs: what does the index return, what type, what shape? Ask about the score range:
is 1.0 perfect match or is 0.0? Ask about the edge case: what should happen when nothing clears the
floor? Ask about the contract: is returning an empty list acceptable, or should the caller raise?

Four questions take thirty seconds. They lock the contract. Now you are building against a
specification, not a guess.

## Narrate While You Code: The ETA Shape

Once you have a contract, state your approach before you type. One sentence on what you are going to
build. Then code it, and narrate each decision as it arrives using the ETA shape: explain the choice
simply, give the technical detail, name the tradeoff.

A narrated decision sounds like this:

> "I'm making `min_score` a constructor argument rather than a parameter on `retrieve()`, because
> the floor is a policy the deployer sets once, not something callers tune per query. The tradeoff
> is that you have to instantiate a new Retriever to change the floor at runtime, but that's
> intentional: you want the policy to be stable across a conversation."

That is thirty seconds. It tells the interviewer you understand the design decision and the reason
behind it. A silent implementation of the same choice tells them nothing.

## The Worked Task: A Retrieval Relevance Floor

Here is what a full narrated screen looks like, from the clarifying questions to the finished
implementation.

---

**The prompt:** "Implement a retriever that wraps a vector index and drops results below a relevance
threshold, so the generator only sees high-confidence context and can refuse when nothing clears the
floor."

### Step 1: Clarify the Contract

Before writing anything, ask:

- "What does the index's `search` method return? A list of tuples, a dataclass, something else?"
- "What is the score range? Is 1.0 a perfect match, or is it 0.0? Are higher scores better or lower?"
- "What should `retrieve()` return when nothing clears the floor: an empty list, or should it raise?"
- "Is it acceptable for the generator to refuse to answer when the list is empty? Or does it need to
  always produce something?"

The answers shape the implementation. Assume the interviewer says: the index returns `(chunk, score)`
tuples, higher is better, the range is 0.0 to 1.0, an empty list is the right return, and yes,
refusing is the intended behavior when nothing clears the floor.

Now you have a contract. State your approach.

### Step 2: State the Approach

> "I'll build a `Retriever` class that wraps any vector index. The floor goes in `__init__` as a
> `min_score` parameter, because it's a deployment policy, not a per-query argument. The `retrieve()`
> method calls the index, filters the results, and returns a list of structured objects with the chunk
> and the score both attached, so the caller can cite sources. If nothing clears the floor, it returns
> an empty list and the generator knows to refuse."

That is the plan. Now build it.

### Step 3: Narrate the Implementation

Start with the data structure the method returns.

```python
from dataclasses import dataclass

@dataclass
class Retrieved:
    chunk: Chunk
    score: float

    @property
    def citation(self) -> str:
        return self.chunk.citation()
```

> "I'm wrapping each result in a `Retrieved` dataclass rather than returning raw tuples. The reason
> is that tuples are positional: whoever calls this has to know that index 0 is the chunk and index 1
> is the score. A dataclass makes the contract explicit and gives us a place to hang the `citation`
> property, so the generator can cite sources without reaching into the chunk internals. The tradeoff
> is one more class to maintain, but the interface clarity is worth it for anything that will get
> reused."

Now the `Retriever` class.

```python
class Retriever:
    def __init__(self, index: VectorIndex, *, min_score: float = 0.0) -> None:
        self._index = index
        self._min_score = min_score

    def retrieve(self, query: str, k: int = 4) -> list[Retrieved]:
        hits = self._index.search(query, k=k)
        return [Retrieved(chunk=c, score=s) for c, s in hits if s >= self._min_score]
```

> "A few things here. `min_score` is keyword-only via the `*` in the signature, so a caller cannot
> accidentally pass it positionally and confuse it with the index. The default is 0.0, which means
> no filtering at all, so the class is a safe drop-in when you do not need a floor. The filtering
> happens in the list comprehension with `if s >= self._min_score`. That single line is the CRAG
> gate: when the index returns low-confidence results, they never reach the generator. If everything
> is below the floor, the list is empty, and that empty list is the signal the generator reads as
> 'refuse to answer.'"

> "The tradeoff of putting the floor in the retriever rather than in the generator is that the policy
> is enforced before the generator ever sees the context. The generator cannot override it. That is
> a feature, not a bug: you want the reliability gate to be structural, not something the model can
> reason its way around."

### Step 4: Name the Edges Before the Interviewer Does

Before the interviewer asks, raise the edge cases yourself.

> "A few things I would test: the zero-results case, where everything is below the floor; the
> all-results case, where the floor is 0.0; and a boundary case where one result is exactly at
> `min_score`, which should pass. I would also think about what happens if the index raises: right
> now that propagates up, which is probably fine, but in production you might want to catch and
> wrap it."

Naming the edges tells the interviewer you know what you built. It is also how you prevent the
"what if the list is empty?" redirect, because you have already answered it.

---

That is a complete narrated screen. The implementation is the same one you would write silently. The
difference is that the interviewer now knows why you made every choice, and they have evidence that
you think about design, contracts, and edge cases, not just syntax.

## Core Concepts

- The technical screen collects a process signal, not an answer key: a narrated, slightly imperfect
  solution scores higher than a silent, correct one because it gives the interviewer something to
  evaluate.
- Clarifying questions before coding are not stalling; they convert an underspecified prompt into a
  contract, and candidates who negotiate the contract always outperform candidates who execute
  against a guess.
- The ETA shape (explain simply, technical detail, tradeoff) is the unit of narration for each
  coding decision; it takes thirty seconds and tells the interviewer you understand the design, not
  just the syntax.
- The four pitfalls of a weak screen are monologuing without check-ins, coding before stating the
  plan, jargon without grounding, and defending a wrong answer when the interviewer hints; all four
  are recoverable if you notice them early.

<div class="claude-handoff" data-exercise="exercises/module4/narrating-the-screen/">

**Try It in Claude Code:** run one coding-screen rep on a small AI-engineering task, narrating your clarifying questions and your reasoning out loud, and log it in your coding-screen log.

</div>
