# Module 3 · Loop Skills
> Source: `skills/`. Reusable skills demonstrating loop-engineering concepts.

## loop-budget
- **Purpose:** Check token budget and run-log spend before and after a loop run. Enforces early exit when over budget or when there is no actionable work.
- **Inputs:** `loop-budget.md` for caps/flags, recent entries in `loop-run-log.md` (last 24h), current state/watchlist.
- **Outputs:** STATE.md notes (on exit), appended JSON run-logs to `loop-run-log.md`, throttling alerts to `loop-budget.md`.
- **Loop principle demonstrated:** Hard budget enforcement and kill-switch early exits before action phases trigger. [THREAD: safety]

## loop-triage
- **Purpose:** Triage recent changes, CI failures, issues, and conversations into a concise, actionable findings report suitable for a loop to consume.
- **Inputs:** Recent CI/test failures, open issues/tickets, recent commits, chat threads, and the current state file.
- **Outputs:** Markdown report categorized into High-Priority Items, Watch Items, Noise/Ignore, and State Updates.
- **Loop principle demonstrated:** Pre-action trigger filtering that separates actionable signal from noise to prevent unnecessary sub-agent spawns.

## loop-verifier
- **Purpose:** Act as an independent verification agent (maker/checker split) that rejects loop-produced changes unless evidence is strong.
- **Inputs:** Implementer's proposal summary and diff, original issue, test/lint commands, and allowed file scope.
- **Outputs:** Markdown verdict (APPROVE, REJECT, ESCALATE_HUMAN) with specific evidence and rejection reasons.
- **Loop principle demonstrated:** Post-action independent verification that defaults to rejection and requires proof of safety before a loop iteration completes.

## minimal-fix
- **Purpose:** Produce the smallest possible code change that fixes a specific, well-scoped issue (CI failure, reviewer comment, typo) without refactoring unrelated code.
- **Inputs:** Exact failure message/comment, implicated files, project build/test commands, and path denylist.
- **Outputs:** Minimal Fix Proposal featuring target, diff summary, verification results, and risk assessment.
- **Loop principle demonstrated:** Scoped, isolated action execution that respects strict boundaries (denylists) and defers final completion status to the verifier.
