# Module 3 · Loop Templates
> Source: `templates/`. Starting points students use when building their own loops.

## `SKILL.md.loop-budget`
**Purpose:** Check token budget and run-log spend before and after a loop run. Enforces early exit when over budget or when there is no actionable work. **What the student fills in:** Actual token caps, pattern IDs, and kill-switch flags specific to their project. **Loop pattern it implements:** Budget guard / kill switch — runs at the start and end of every loop iteration to enforce spending limits and early-exit conditions.

## `SKILL.md.loop-triage`
**Purpose:** Triage recent changes, CI failures, issues, and conversations. Produces a concise, actionable findings report suitable for a loop to consume and writes structured output to a state file or Linear board. **What the student fills in:** Project-specific skills, conventions, and context provided at runtime. **Loop pattern it implements:** Trigger / observation — the "eyes" of the loop that produces a prioritized, actionable list of items.

## `SKILL.md.minimal-fix`
**Purpose:** Produce the smallest possible code change that fixes a specific, well-scoped issue (CI failure, reviewer comment, typo). Used only when the fix target is explicit. **What the student fills in:** Exact failure message, implicated files, project build/test commands, and path denylists. **Loop pattern it implements:** Action — the maker in a maker/checker split that generates a minimal, scoped diff to address an issue.

## `SKILL.md.verifier`
**Purpose:** Independent verification agent for loop-produced changes that finds reasons to reject, runs tests, and confirms diff scope. Used after minimal-fix or any implementer sub-agent. **What the student fills in:** Allowed file scope, project test/lint commands, and original issue context. **Loop pattern it implements:** Verification — the checker in a maker/checker split that rejects changes unless evidence is strong.

## `STATE.md.template`
**Purpose:** Track the current state of the loop including high-priority items, a watch list, and recent noise. Updated by the loop on each run. **What the student fills in:** Project name, specific high-priority items, and human decisions. **Loop pattern it implements:** State management — shared memory between loop runs and humans for handoffs and tracking.

## `loop-budget.md.template`
**Purpose:** Define daily limits (max runs, tokens, sub-agent spawns) for each loop pattern, along with procedures for budget exceedance and kill switch activation. **What the student fills in:** Actual daily limits per loop pattern and project-specific kill switch commands. **Loop pattern it implements:** Budget configuration — establishes hard limits and kill switch mechanisms for safe loop execution.

## `loop-run-log.md.template`
**Purpose:** Append one JSON entry per loop run to maintain an auditable history of runs, durations, findings, actions, and token spend. Entries are pruned after 30 days. **What the student fills in:** Nothing (maintained automatically by the loop). **Loop pattern it implements:** Audit log — structured run history for budget tracking and verification.

## `pattern-template.md`
**Purpose:** Define a complete loop pattern including scheduling, required skills, state schema, typical cycle, verification strategy, human handoff points, and failure modes. **What the student fills in:** Pattern name, goal, scheduling commands, required skills, state schema, cycle steps, verification rules, human gates, tool-specific notes, and failure mitigations. **Loop pattern it implements:** Full loop architecture — trigger, action, verification, and budget/human handoff integration for a specific recurring task.
