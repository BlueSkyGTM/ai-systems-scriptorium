# The Clock and the Weak-Screen Audit

The clock is not a countdown to the answer. It is part of what the interviewer is testing. A candidate who runs out of time with nothing runnable has not just failed to finish; they have told the interviewer that they cannot prioritize under pressure. A candidate who says "I have about four minutes left, so I am going to cut error logging and mark it as a known gap" has just demonstrated production judgment.

That is the seam this lesson teaches: how to manage the clock as a resource and how to audit your own screen performance before the room does it for you.

## Allocate the Clock Before You Touch the Keyboard

The single highest-leverage move in a timed screen is deciding, out loud, before you start coding, how you will spend your time.

The allocation follows the same shape every time.

**Clarify (two to three minutes).** Ask the questions you cannot infer from the prompt. Not every question you could ask; the load-bearing ones. What is the interface this component will plug into? Is there an existing type I should conform to? Is the error case in scope for this session, or do you want the happy path first? Then restate what you heard: "So I am building a read-only kill switch that the agent loop checks before each action; the operator trips it from outside the process; I do not need to test the write path today." That restatement earns you alignment and gives the interviewer a chance to correct a wrong assumption before you have coded against it.

**Happy path (roughly half the clock).** The first version runs and is demonstrably correct on the main case. Not clean; not hardened; just runnable on the case that matters. This is the artifact. If the clock expires here, you have something to show.

**Edges and polish (the remaining time).** Error cases, input validation, a docstring, a test. You work these in priority order, and you say which ones you are taking in priority order: "I want to add input validation on the score parameter, then a test for the breach case; if I run out of time before the test I will note it as the next step."

Narrate the budget out loud. Not once at the start and then silently; at each transition. "I have about ten minutes left; the main path works; I am moving to the breach case now." The interviewer tracks your clock awareness; silence reads as lost.

## The Stated Cut

When the clock is short, the move is not to code faster. It is to name what you are not building and why.

The stated cut beats silent incompletion on every metric. A silent omission looks like you forgot it or did not know it needed to be there. A stated cut looks like judgment. "I am skipping input validation for now; in production you would want to reject a score outside zero to one, but I want the breach logic running first" is an engineer reasoning about priority. That is what the screen is measuring.

The cut must be narrated at the moment you make it, not at the end as an apology. Say it when you decide to skip the thing, not after you have run out of time. An apology after the clock expires is not a cut; it is an admission.

## The Read-Only Kill Switch

The prompt: "Build a kill switch the agent loop can check before each action. The agent must only be able to read it, never write it."

You hear the prompt. You clarify.

"So the interface constraint is the key part of this task: the agent gets a read-only handle. Where does the switch live in storage? Can I use a file path for this session?" The interviewer confirms: a file path is fine; the read-only boundary is what matters.

You state your time plan: "I have about fifteen minutes. I want a working `tripped()` check in five, then I will design the operator-vs-agent split, then a quick test."

You lead with the core idea before the code:

"The property this pattern enforces is asymmetric control. The agent's reachable state does not include the write path. If it did, a sufficiently autonomous agent could disable its own kill switch, and you have a safety control in name only. The split between `KillSwitch` and `OperatorKillSwitch` is where that property lives."

Then you code. The agent's handle:

```python
class KillSwitch:
    """Read-only from the agent's side. The operator holds the write path."""

    def __init__(self, path: str):
        self._path = path

    def tripped(self) -> bool:
        """The only method the agent loop calls."""
        return os.path.exists(self._path)
```

You narrate as you write: "The agent loop is handed an instance of `KillSwitch`, not `OperatorKillSwitch`. It gets `tripped()` and nothing else. There is no `engage()` in this class because the agent must never be able to call it."

Then the operator handle:

```python
class OperatorKillSwitch(KillSwitch):
    """The operator's handle. The agent never gets one of these."""

    def engage(self, reason: str = "operator halt") -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            f.write(reason)

    def clear(self) -> None:
        if os.path.exists(self._path):
            os.remove(self._path)
```

"The operator creates the `OperatorKillSwitch`, keeps the reference, and passes only the base class to the agent loop constructor. The agent cannot call `engage()` because it does not have a reference to the subclass. The access control is enforced by the object graph, not by instructions to the model."

You have the happy path in about six minutes. You check in: "That is the core design. I want to add a `Halted` exception the loop raises when `tripped()` returns true, then a minimal test. Do you want me to go deeper on the storage layer, or should I keep moving to the test?"

The interviewer says keep moving. You raise the exception, write one test that trips the file and asserts `tripped()` returns true, then one test on a fresh path that asserts it returns false. Clock used: eleven minutes. Four minutes to spare, which you spend noting the production analogue out loud: "In production this would be a Redis key under a read-only ACL, or a feature flag the agent process has read access to but cannot write. The file is the stand-in; the asymmetric control property is the same."

That last sentence is not filler. It is the signal that you understand what the pattern is abstracting.

## The Drift Monitor

The prompt: "Build a quality drift monitor. It should track a rolling window of quality scores and flag when the mean falls below an SLO floor."

You clarify: "What is the interface for the SLO floor? Is it a fixed constant, or does it come from a baseline measurement? What type do you want the output to be?" The interviewer says the floor derives from a baseline at deploy time; return a structured reading with the current mean and a breach flag.

You state your plan: "I have about twenty minutes. I want a `record()` method that returns a reading in ten, then I will add the `baseline` and `floor` derivation, then test the breach case."

You narrate the design decision before touching the keyboard:

"The key question here is what the floor is measuring against. A point check asks whether any single score is below a threshold. A rolling mean asks whether quality is trending down, which is a different, and usually more useful, question in production. A single bad score is noise; a degraded rolling mean is signal."

```python
from collections import deque
from dataclasses import dataclass

@dataclass
class DriftReading:
    n: int
    rolling_mean: float
    baseline: float
    floor: float
    breached: bool
```

"I am separating the reading from the monitor because the monitor accumulates state and the reading is a snapshot. That makes the reading easy to log, compare, or pass to an alerting system without coupling it to the monitor."

```python
class DriftMonitor:
    def __init__(self, baseline: float, *, window: int = 20, tolerance: float = 0.15) -> None:
        self.baseline = baseline
        self.floor = max(0.0, baseline - tolerance)
        self.window = window
        self._scores = deque(maxlen=window)

    def record(self, score: float) -> DriftReading:
        self._scores.append(float(score))
        mean = sum(self._scores) / len(self._scores)
        return DriftReading(
            n=len(self._scores),
            rolling_mean=mean,
            baseline=self.baseline,
            floor=self.floor,
            breached=mean < self.floor,
        )
```

You narrate the `floor` line: "The floor is `baseline minus tolerance`, clamped to zero. If the baseline is 0.9 and tolerance is 0.15, the floor is 0.75. The operator sets the tolerance, not the floor directly, because the tolerance is the meaningful knob: how much degradation from what we measured at deploy is acceptable?"

You check in with nine minutes left: "The happy path runs. I want to test the breach case, then note one known gap. Should I also show a degrading run?"

The interviewer says yes. You write a quick inline demo:

```python
mon = DriftMonitor(baseline=0.9, window=5, tolerance=0.2)
for s in [0.9, 0.9, 0.8, 0.4, 0.3]:
    r = mon.record(s)
    status = "BREACH" if r.breached else "ok"
    print(f"n={r.n} mean={r.rolling_mean:.2f} floor={r.floor:.2f} -> {status}")
```

"As the window fills with low scores, the mean eventually falls below 0.7 and the breach flag trips. The monitor does not raise an exception; it returns a reading. The caller decides what a breach means: alert, roll back, page someone. That keeps this component composable."

You are at seventeen minutes. You state the cut: "I am skipping input validation on `score`; in production you would want to reject values outside zero to one and log the bad input, but I want to leave two minutes to cover the production analogue." The interviewer nods. You spend those two minutes: "In a live system, this monitor runs as a sidecar or a service, sampling a scored quality signal from traffic. The `baseline` comes from the last eval run before deploy. The `tolerance` is an SLA negotiation between product and eng. Silent degradation is the failure mode this catches; no infrastructure metric would have moved."

Clock: clean.

## The Weak-Screen Audit

The module overview said this module builds the communication layer, and the communication layer is not just what you do during the screen. It includes what you do immediately after: run the audit on yourself before the feedback comes to you.

The weak-design audit in Module 5 turns a design session's failure modes into a structured self-check. This is the coding-screen analogue. After every logged rep, run through these questions. For each one, give yourself a pass or a gap, and record the gap.

### Clarification

**"Did I clarify before coding, or did I assume?"**

Pass: you asked at least one load-bearing clarifying question and restated the scope before you started. The restatement is part of the check, not optional.

Gap: you started coding based on the literal prompt text and had to course-correct mid-task when you discovered an ambiguity. That course-correction cost you time and told the interviewer you do not treat underspecified prompts as underspecified.

### Narration

**"Did I narrate, or did I go silent?"**

Pass: the interviewer could follow your reasoning at every step without asking. You said why before you said what.

Gap: there were stretches where you coded in silence. Even if the code was good, the interviewer had nothing to evaluate. Silence in a screen is not concentration; it reads as a signal that you are lost or that you do not understand the communication requirement.

### Structure

**"Did I lead with structure?"**

Pass: you stated the design decision before you wrote the first line. The interviewer knew where you were going before you arrived.

Gap: you dove into code and the architecture emerged from the bottom up. The interviewer had to reverse-engineer your approach from the code you were writing. That is asking them to do your job.

### Testing

**"Did I test as I went, or only at the end?"**

Pass: you ran or sketched a test before moving to the next section. You found a bug while the relevant code was still in focus and fixed it there.

Gap: you wrote all the code and then ran everything at the end. When something broke, you had to retrace the whole session to find the failure point. That is a debugging problem you created for yourself, and the interviewer watched you create it.

### Debugging

**"When stuck, did I debug out loud or freeze?"**

Pass: you hit a bug, you stated the three hypotheses about its cause, you isolated it, and you fixed it without rewriting the whole function.

Gap: you went quiet when something broke. The silence lasted more than thirty seconds. The interviewer could not distinguish "working through it" from "lost." When you broke silence, it was to say the fix, not to narrate the diagnosis.

### Updating

**"When the interviewer hinted I was wrong, did I update or defend?"**

Pass: the interviewer's question or frown registered as signal. You paused, you said "let me reconsider that," and you updated your approach. The update did not require them to tell you twice.

Gap: you defended your first answer. You explained why your approach was correct, then continued with it, and the interviewer's skepticism escalated. Defending a wrong answer is a worse signal than getting it wrong.

### Clock

**"Did I manage the clock, or did I run out with nothing runnable?"**

Pass: you allocated the time at the start, narrated transitions, made at least one stated cut, and had a working artifact when the clock stopped.

Gap: you ran out of time without a runnable happy path. The final state was a partial implementation the interviewer could not evaluate. No amount of explanation after the fact recovers this; the artifact is the evidence, and the artifact was not there.

## Core Concepts

- Narrating the time budget at the start and at each transition is a screen skill, not a formality; silence on the clock reads as lost.
- The stated cut beats silent incompletion: naming what you are not building, and why, is a signal of production judgment, not an excuse.
- Asymmetric control means the agent's reachable state does not include the write path; the kill switch works because the agent cannot touch the class that has `engage()`.
- The weak-screen audit runs on your logged rep immediately after, not after you get feedback; the seven questions span clarification, narration, structure, testing, debugging, updating, and clock management.

<div class="claude-handoff" data-exercise="exercises/module4/the-clock-and-the-weak-screen-audit/">

**Try It in Claude Code:** run a timed coding-screen rep, then run the weak-screen audit on it and record which checks you passed, which you missed, and the one habit you will change, in your coding-screen log.

</div>
