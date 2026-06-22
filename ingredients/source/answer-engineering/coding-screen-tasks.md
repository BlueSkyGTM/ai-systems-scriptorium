# Coding-Screen Tasks — M4 Reference Ingredient

The grounded worked-task catalog for Module 4 "Technical Screens" plus the communication-layer spine.
Every coding task below is drawn from REAL, already-tested Sans Python portfolio code; the cited file is
the reference implementation that grounds the task (no fabricated problems). Lesson-writers: READ the
cited file for the exact pattern you show; teach the reasoning and the narration, not a paste-ready
solution. Date: 2026-06-21.

The module's thesis: a technical screen tests how you think, not whether you finish. The transferable
skill is the **communication layer** (clarify, narrate, debug out loud, test as you go). The tasks are
how that skill is taught, on real AI-engineering patterns.

## The Communication Spine (from asdg 00-interview-prep)

- **ETA, for narrating a choice** (asdg 02-answer-frameworks, "Concept Explanation Framework"):
  Explain simply (one sentence) -> Technical detail -> Applications and tradeoffs. Use it to narrate why
  you are making each coding decision out loud.
- **The debugging motion** (asdg 02-answer-frameworks, "Debugging and Troubleshooting Framework"): gather
  information -> form 3-5 hypotheses -> diagnose (isolate, trace) -> propose a fix + a verification. This
  is how you debug OUT LOUD when stuck, instead of going silent.
- **Communication pitfalls** (asdg 03-common-pitfalls 11-14): monologuing without check-ins; not leading
  with structure; jargon without explanation; defending a wrong answer instead of updating when the
  interviewer hints. These are the weak-screen failure modes.
- **Time management** (asdg 03-common-pitfalls 16): allocate the clock; clarify briefly, code the happy
  path first, then defensive cases; do not spend all the time polishing one corner.

## The Grounded Tasks

Each: premise, the real reference file (under `library/completed/sans-python/exercises/module6/`),
the pattern, why it is an AI-engineering screen task (not LeetCode), and rough difficulty.

### Task A — Retrieval relevance floor (CRAG gate)
- **Premise:** wrap a vector index in a retriever that drops results below a `min_score` so the generator
  only sees high-confidence context and can refuse when nothing clears the floor.
- **Reference:** `02-production-rag-chatbot/retriever.py` (the `Retriever` class, `min_score` filter,
  `retrieve()` returning `Retrieved` with citations).
- **Why a screen task:** RAG reliability; "how do you know when NOT to answer?"; why the floor lives in
  the retriever, not the generator. Difficulty: warm-up.

### Task B — Token-budget guard (dual caps)
- **Premise:** a cost governor enforcing a dollar ceiling AND an iteration cap, checked BEFORE each model
  call (deterministic, no model judgment), raising when either is breached.
- **Reference:** `01-terminal-coding-agent/budget.py` (the `Budget` class: `check()`, `charge()`,
  `_enforce()`, `remaining_usd()`).
- **Why a screen task:** Denial-of-Wallet; why the check is before the call, not after; why enforcement is
  deterministic code, not a model instruction. Difficulty: warm-up.

### Task C — Content guardrail with a hardcoded floor
- **Premise:** a deterministic input/output screen that matches against hardcoded prohibition patterns and
  returns a structured `Verdict`; operator-tunable rules sit ABOVE the floor and cannot lower it.
- **Reference:** `02-production-rag-chatbot/guardrail.py` (`_PROHIBITED`, `_classify()`,
  `screen_input()`/`screen_output()`, `Verdict`).
- **Why a screen task:** safety must be deterministic and enforcer-controlled; how to layer a model
  classifier on top without letting it override the floor. Difficulty: warm-up/standard.

### Task D — Subprocess sandbox with a wall-clock timeout
- **Premise:** run a test suite in a child process under a deadline; capture the result as structured data;
  treat a timeout as a RESULT (recoverable), not an uncaught error.
- **Reference:** `01-terminal-coding-agent/sandbox.py` (`SandboxResult`, `run()` with
  `subprocess.TimeoutExpired`, `run_pytest()`).
- **Why a screen task:** agents that execute code must isolate it; timeout semantics; partial-output
  capture. A natural DEBUGGING task: "the run hangs; diagnose and fix." Difficulty: standard.

### Task E — Tool dispatch with path jailing
- **Premise:** a tool registry that validates arguments against a schema, resolves paths so they cannot
  escape the project root, and returns errors as observations (data the model reads) rather than
  exceptions that crash the loop.
- **Reference:** `01-terminal-coding-agent/tools/__init__.py` (`TOOL_SCHEMAS`, `_resolve()` path jail,
  `_validate()`, `dispatch()`).
- **Why a screen task:** path-traversal defense; contract validation; error-as-observation. A natural
  DEBUGGING task: "a crafted path escapes the jail; find and fix it." Difficulty: standard/stretch.

### Task F — Read-only kill switch (asymmetric control)
- **Premise:** a kill switch the agent can only READ (`tripped()`), never write, so it cannot disable its
  own stop; the operator holds the write path.
- **Reference:** `01-terminal-coding-agent/killswitch.py` (`KillSwitch` vs `OperatorKillSwitch`; the
  read-only boundary via the interface).
- **Why a screen task:** asymmetric control as a design property, not a hope; why the off switch must live
  outside the agent's reachable state. Difficulty: warm-up/standard.

### Task G — Quality drift monitor (rolling window + SLO)
- **Premise:** a rolling-window quality metric that flags when the mean falls below an SLO floor; return a
  reading with the mean, the baseline, and a breach flag.
- **Reference:** `02-production-rag-chatbot/drift.py` (`DriftMonitor` with `baseline`, `floor`, `window`;
  `record()`; `DriftReading.breached`).
- **Why a screen task:** silent production degradation; rolling window vs point check; baseline vs floor;
  when to alert. Difficulty: standard.

### Task H — Offline eval gate (RAG triad)
- **Premise:** run a chatbot over a labeled set, score retrieval precision + answer faithfulness, return a
  pass/fail against acceptance thresholds; default to FAIL.
- **Reference:** `02-production-rag-chatbot/eval.py` (`load_evalset()`, `_faithful()`, `evaluate()`,
  `EvalReport.passes()`).
- **Why a screen task:** evals gate deploys; deterministic scoring; why default-FAIL. Difficulty:
  standard/stretch.

## Suggested lesson-to-task map (locked in m4/PLAN.md)

- L1 `narrating-the-screen` (the communication layer): Task A as the narrated warm-up.
- L2 `the-happy-path-and-the-edges`: Task B + Task C.
- L3 `debugging-out-loud`: Task D (timeout hang) + Task E (path-jail bug).
- L4 `the-clock-and-the-weak-screen-audit`: Task F + Task G.
(Task H is reserve / stretch material.)

## The coding-screen log (the M4 throughline artifact)

`exercises/prep/coding-screen-log.md`, entries `## Screen <n>`, fields:
**Task:** / **Clarifying questions:** / **Approach narration:** / **Stuck and recovery:** /
**Test cases:** / **Verdict:**. Gated by `check_prep.py --module 4`.

## Honest scope (carry into the lessons)

M4 teaches the communication layer + real AI-engineering coding patterns. It is NOT a substitute for
dedicated algorithm/data-structure drilling; M8 already tells the reader to source that separately, and
M4 keeps that line. The grounded tasks here are realistic AI-eng screen problems, not a LeetCode set.
