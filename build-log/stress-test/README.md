# Stress-Test: Does the Method Complete the Books?

Definition of, and documentation for, the stress-test experiment (this README is its self-contained spec; the original root `HANDOFF.md` that launched it has been retired). The question is not "did the books get made" but
**which part did the work — the Scriptorium's structure (deferred-context routing + contracts + gates +
spawn-and-collapse) or Claude's built-in capability?** A cold agent + one `CLAUDE.md` is the baseline; this folder
records the delta over that baseline, honestly.

## Files to write here

- `FINDINGS.md` — the running verdict: is the theory holding, and where is value attributable to structure vs.
  built-ins? Update as you go. Use the verdict scale below.
- `<book>.md` — one per book you touch (e.g. `just-python.md`, `machine-math.md`): the per-book log using the
  template below.

## Per-book / per-module template

- **Stage touched:** e.g. Just Python M2, plan + author.
- **Cold-proceed?** Y/N + evidence: could you act from structure alone, no human re-brief?
- **Structure did:** specific — deferred load/don't-load, route-lint catches, contract enforcement, gate stops,
  spawn isolation.
- **Baseline would have done:** honest — what plain Claude + one `CLAUDE.md` gets you anyway.
- **Net attributable to structure:** the delta between the two above.
- **Strain / overhead:** where the method cost more than it returned.
- **Context economy:** did you stay lean (a boundary's slice, not the 767MB vault)?
- **Drift caught:** errors route-lint or the contracts caught that an eye would have missed.

## Verdict scale (in `FINDINGS.md`)

`HOLDS` / `PARTIAL` / `MOSTLY-BUILT-IN` — each with the evidence. A negative result is a real result. Do not
flatter the method.
