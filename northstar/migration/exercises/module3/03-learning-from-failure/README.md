# Exercise: Learning from Failure

## Goal

Extend `module3-agent/` with a Reflexion layer — an episodic memory buffer, a Self-Reflector that writes a verbal lesson after each failure, and a CRITIC-style stop condition that passes only when an external verifier confirms the output.

## Why

Agents that repeat failures waste tokens and produce worse results; routing verification through an external check that the model cannot hallucinate around is the 2026 production pattern for iterative improvement.

## Steps

1. Add `module3-agent/reflexion.py` containing:
   - `EpisodicMemory`: a list of `{trial: int, failure_reason: str, reflection: str}` entries. Expose `add(trial, failure_reason, reflection)` and `as_context() -> str` (formats all stored reflections as a bulleted list the agent prepends to its next attempt).
   - `SelfReflector(goal, attempt, failure_reason) -> str`: a stub that takes the goal, the failed attempt text, and a reason string, and returns a one-sentence verbal lesson. (Stub: return `f"On trial {trial}: avoid {failure_reason}."` — the stretch goal replaces this with a real LLM call.)
   - `reflexion_loop(goal, max_trials, verifier)`: runs up to `max_trials` attempts. Each attempt calls the base `agent_loop` from `loop.py`. After each attempt, calls `verifier(output) -> (passed: bool, reason: str)`. If the verifier passes, return the output. If it fails, call `SelfReflector`, store the reflection in `EpisodicMemory`, and prepend `memory.as_context()` to the goal for the next trial.
2. Implement a stub verifier: `length_verifier(output) -> (bool, str)` — passes if the output contains at least 50 characters, fails with `"output too short"` otherwise. This stands in for a real external check.
3. Rig the first trial to fail: make the stub model return a one-word answer on trial 1, a full sentence on trial 2.
4. Run `reflexion_loop` with `max_trials=3` and `length_verifier`. Print for each trial:
   - `[Trial N] Output: ...`
   - `[Trial N] Verifier: passed/failed — reason`
   - `[Trial N] Reflection: ...` (only on failure)
   - The memory context prepended to the next trial's goal.
5. Verify that the reflection from trial 1 appears in the goal context for trial 2.

## Done when

- `module3-agent/reflexion.py` exists and runs without errors.
- Trial 1 fails, generates a reflection, stores it in `EpisodicMemory`.
- Trial 2 receives the reflection in its goal context (printed before the agent runs).
- Trial 2 passes the verifier and the loop exits with the final output.
- No third-party reflexion library is imported.

## Stretch

Replace the stub `SelfReflector` with a real LLM call: give the model the goal, the failed output, and the failure reason, and ask it to write a one-sentence rule to avoid the failure. Replace `length_verifier` with a `code_verifier` that runs `exec()` on generated Python code and passes only if no exception is raised. Run against a code-generation task — ask the agent to write a function that reverses a string, verify by executing it, and observe how many trials it takes to converge.
