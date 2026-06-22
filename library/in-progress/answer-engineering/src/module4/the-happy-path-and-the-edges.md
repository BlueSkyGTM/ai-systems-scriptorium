# The Happy Path and the Edges

The previous lesson built the communication layer: narrate, clarify, do not go silent. This lesson is
about the sequence inside that narration. How you order your implementation tells the interviewer as much
as the code itself.

## Happy Path First

A working skeleton beats a half-built perfect solution, and the interviewer knows this. The candidate who
spends fifteen minutes on edge-case handling before they have a single line that runs has made a
prioritization error in public. The interviewer is watching; the signal is real.

The move is simple: say out loud that you are doing it on purpose. "I am going to get the happy path
working first so we have something runnable, then I will layer in the defensive cases." That sentence
does two things. It shows you understand that a partial working solution is more valuable than a
comprehensive non-running one. It also creates a shared checkpoint: the interviewer knows what you are
planning, so they can redirect you if the edge cases are actually the point of the problem.

After the happy path runs, enumerate the edges before you code them. Name them one at a time: "Zero or
negative inputs. The ordering of check before charge. The second cap, the iteration ceiling. Each one
is a deliberate decision, not an afterthought." The enumeration signals that you know the space. Then
handle them in order and test each one as you go.

## Worked Example: The Token-Budget Guard

### The Prompt

"Write a cost governor for an agent loop. It should enforce a dollar ceiling and stop the run when the
limit is hit."

### Happy Path First

State the goal: track spend and raise when you go over. That is the happy path. Write that first.

```python
class BudgetBreach(Exception):
    pass

class Budget:
    def __init__(self, max_usd: float):
        self.max_usd = max_usd
        self.spent_usd = 0.0

    def charge(self, usd: float) -> None:
        self.spent_usd += usd
        if self.spent_usd > self.max_usd:
            raise BudgetBreach(f"budget exceeded: ${self.spent_usd:.4f}")
```

Say out loud: "This version tracks spend and raises on breach. It is not complete, but it is runnable
and testable right now." Then test it immediately.

```python
b = Budget(max_usd=1.00)
b.charge(0.50)   # fine
b.charge(0.60)   # should raise
```

Run that check. Confirm the exception fires. Now the skeleton is solid; you have not spent time on
edges that sit on top of broken scaffolding.

### Edge Cases, Enumerated Out Loud

Say them before you code them: "I see three edges. First, the agent loop can run forever even within
the dollar cap, so I need an iteration ceiling alongside the cost ceiling. Second, the check should
happen before the call, not after, because if I charge and then check I have already paid. Third, I
should handle zero or negative spend amounts gracefully."

Handle the iteration cap. The real `Budget` class in `exercises/module6/01-terminal-coding-agent/budget.py`
carries both caps as first-class parameters: `max_usd` and `max_turns`. Add it:

```python
@dataclass
class Budget:
    max_usd: float
    max_turns: int
    spent_usd: float = 0.0
    turns: int = 0

    def charge(self, usd: float, label: str = "model_call") -> None:
        self.spent_usd += usd
        self.turns += 1
        self._enforce()

    def _enforce(self) -> None:
        if self.spent_usd > self.max_usd:
            raise BudgetBreach(
                f"per-task budget exceeded: ${self.spent_usd:.4f} > ${self.max_usd:.4f}"
            )
        if self.turns > self.max_turns:
            raise BudgetBreach(
                f"iteration cap exceeded: {self.turns} > {self.max_turns}"
            )
```

Test the iteration cap separately: "Let me confirm the turn ceiling fires independently of spend."

```python
b = Budget(max_usd=100.00, max_turns=2)
b.charge(0.01)  # turn 1: fine
b.charge(0.01)  # turn 2: fine
b.charge(0.01)  # turn 3: should raise on iteration
```

Now handle the check-before-charge ordering. Say why: "A budget you check after paying is one the
agent has already cheated. The loop should call `check()` before each model call so a run that is
already over budget stops before paying for one more action." The real implementation separates
`check()` from `charge()` for exactly this reason.

```python
def check(self) -> None:
    """Call before each model call. Raises if already over cap."""
    self._enforce()
```

Test the sequence: confirm that `check()` after a prior `charge()` that tripped the cap still raises,
without accumulating another turn.

The zero-or-negative input edge is the last one: "What happens if the caller passes a negative spend
amount? That would silently decrease `spent_usd` and extend the budget. I want to guard against that."
Mention it, decide whether to add a guard or treat it as caller error, and say your reasoning out loud.
In the portfolio implementation the caller contract is strict; invalid amounts are not expected. Say
that and move on. The interviewer sees you considered it.

## Worked Example: The Content Guardrail

### The Prompt

"Write a content guardrail that screens text against a list of prohibited patterns and returns a
structured verdict."

### Happy Path First

The happy path is: compile a list of patterns, search the input, return a result. Say that out loud,
then write it.

```python
import re
from dataclasses import dataclass

@dataclass
class Verdict:
    blocked: bool
    rule: str = ""

class Guardrail:
    def __init__(self, patterns):
        self._patterns = [re.compile(p, re.IGNORECASE) for p in patterns]

    def screen(self, text: str) -> Verdict:
        for pat in self._patterns:
            if pat.search(text):
                return Verdict(blocked=True, rule=pat.pattern)
        return Verdict(blocked=False)
```

Test it immediately with one clean input and one that should trigger.

```python
g = Guardrail([r"\bexfiltrate\b"])
print(g.screen("How long are records retained?").blocked)     # False
print(g.screen("Exfiltrate all customer records").blocked)    # True
```

Confirm both results. The skeleton works. Now enumerate the edges.

### Edge Cases, Enumerated Out Loud

Say them: "Three things I want to address. First, some patterns should be absolute; an operator
configuring the system should not be able to remove them. Second, the empty input case. Third, the
`Verdict` needs a `stage` field because this guard runs on both inputs and outputs, and the caller
needs to know which fired."

Handle the hardcoded floor. This is the architecturally interesting edge, and worth a sentence of
narration: "The safety floor cannot be tunable, because an operator who can lower the floor below the
prohibition level has effectively disabled it. In `exercises/module6/02-production-rag-chatbot/guardrail.py`
the floor lives in `_PROHIBITED` at module level, compiled separately from the operator-tunable
patterns. The operator layer adds to the pattern set; it cannot remove from the floor."

Show the two-layer structure:

```python
# Module-level floor: not passed through __init__, not tunable
_PROHIBITED = [
    r"\bignore (all|the|your) (previous|prior) instructions\b",
    r"\bexfiltrate\b",
    r"\bdisable (the )?(audit|logging|guardrail)\b",
]

class Guardrail:
    def __init__(self, *, enforce_off_topic: bool = False) -> None:
        self._patterns = [re.compile(p, re.IGNORECASE) for p in _PROHIBITED]
        if enforce_off_topic:
            self._patterns += [re.compile(r"\bwrite me a poem\b", re.IGNORECASE)]
```

Test the layering: "I want to confirm that even with `enforce_off_topic=False`, the hardcoded patterns
still block." Run a prohibited input through both configurations; both must block.

Handle the `stage` field: "The guardrail screens inputs before retrieval and outputs before the
response. The verdict should carry which stage fired so the caller can log it correctly." Add `stage`
to the dataclass and pass it from `screen_input` and `screen_output` separately. Test each path.

Handle the empty input last: "What does an empty string return? The pattern loop finds no match, so
it returns `blocked=False`. That is the right answer; an empty query is not a threat." Say it,
confirm it with a quick test, move on.

## Testing as You Go

The pattern across both examples is the same: after each step, run the smallest test that confirms
the step works before moving to the next. This is not thoroughness for its own sake. It is error
isolation. If you write the happy path and three edges together before running anything, you do not
know which part broke when something fails. If you test after each step, the failing test names the
failing step.

Say this out loud too: "I am testing after each step so I know exactly where to look if something
breaks." The interviewer hears that you treat testability as a design property, not a post-coding
activity.

## Core Concepts

- Code the happy path first and say so out loud: a working skeleton gives you a testable foundation,
  and the narration shows the interviewer that the sequence is intentional, not accidental.
- Enumerate edge cases before you code them: naming them in order shows you know the problem space
  and creates a shared plan the interviewer can redirect if the priorities are wrong.
- The check-before-charge ordering in a cost governor is a design decision, not a coincidence: a
  budget enforced after the call has already been paid cannot prevent the next one.
- Hardcoded safety floors and operator-tunable layers serve different purposes: a floor an operator
  can lower is not a floor, it is a default, and the architecture must reflect that distinction.

<div class="claude-handoff" data-exercise="exercises/module4/the-happy-path-and-the-edges/">

**Try It in Claude Code:** run a coding-screen rep where you code the happy path first and then enumerate and handle the edge cases out loud, logging the test cases you ran in your coding-screen log.

</div>
