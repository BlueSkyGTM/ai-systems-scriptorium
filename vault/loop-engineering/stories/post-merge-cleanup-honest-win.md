# Post-Merge Cleanup — small wins without the babysitter tax

**Pattern:** [post-merge-cleanup](../patterns/post-merge-cleanup.md)  
**Cadence:** 1d (off-peak)  
**Outcome:** Useful, low-noise follow-up PRs — not a magic janitor

## Context

After shipping a feature branch, the team had predictable leftovers: stale comments, half-updated docs, and tiny lint issues that nobody wanted to context-switch for. PR Babysitter felt too heavy for work already on `main`.

## What we ran

- **Loop:** daily post-merge scan on the last 24–48h of merges
- **Skills:** `post-merge-scan`, `minimal-fix`, `loop-verifier`
- **State:** `post-merge-state.md` with “fixed / ticketed / ignored” per merge
- **Week one:** L1 report only — the loop listed candidates, humans picked two

## What worked

- Off-peak cadence avoided fighting active feature work
- State file prevented re-scanning the same merge three days in a row
- Verifier caught a “doc fix” that secretly changed a public API example

## What we learned

- The loop over-triaged bot-authored merge commits — we added a ignore list in state
- Anything touching `auth/` or `payments/` stayed human-only (denylist in LOOP.md)
- Two people got value from the **report** alone without enabling L2 auto-fix

## Recommendation

Start L1 for two weeks. If the report is consistently right, enable L2 for docs and comment-only paths. Keep architectural debt in Linear, not in the loop.