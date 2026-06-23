# Backlog — open cross-cutting items

Only what is still open. Resolved items live in git history and `build-log/`; they were pruned from here
2026-06-21 to keep the focus on book building.

## Publish-time (gated at `GATE-PUBLISH`; private-first until then)

- **Vercel deploy** — `vercel.json` is ready and locally validated. Remaining is Ray's dashboard work:
  import `BlueSkyGTM/ai-systems-scriptorium`, build, move the subdomain onto it, verify.
- **Set `book.toml` `git-repository-url`** — only when the repo goes public (else it 404s for visitors).

## Quality

- **Commit runnable test harnesses for Just Python and Local Metal** — both ship their code only as
  lesson prose (no committed `.py`, no tests), so correctness is unverifiable except by reading. The
  2026-06-22 QC pass found exactly the drift a committed harness would catch (Just Python: an M7
  confusion-count example plus M6/M8 prose-vs-code mismatches; Local Metal: the router silently
  ignoring its advertised `latency_budget_ms` signal). Sans Python and Answer Engineering already
  commit passing gates (AE runs 89 tests); bring these two up to that bar.

## Lab

- **Name the permanent Enhancers shelf** once Open Brain (the first production enhancer) completes; until
  then enhancers live in `extra-credit/` (`experiments/` → `production/`).
