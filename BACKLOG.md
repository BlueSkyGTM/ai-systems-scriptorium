# Backlog — open cross-cutting items

Only what is still open. Resolved items live in git history and `build-log/`; they were pruned from here
2026-06-21 to keep the focus on book building.

## Publish-time (gated at `GATE-PUBLISH`; private-first until then)

- **Vercel deploy** — `vercel.json` is ready and locally validated. Remaining is Ray's dashboard work:
  import `BlueSkyGTM/ai-systems-scriptorium`, build, move the subdomain onto it, verify.
- **Set `book.toml` `git-repository-url`** — only when the repo goes public (else it 404s for visitors).

## Strategic (deferred)

- **Bot Bottega** — extract the engine (gates + orchestration + the contract pattern + optional ICM) as a
  cloneable starter, so a new repo never starts from scratch. The Scriptorium is its reference instance.
  Pending Ray's decision on the unifying thread ("onboard the agent into the gig, then get out of its
  way") and whether to build it. Captured in the session record + auto-memory.
- **Stub books** — `library/planned/show-dont-tell` and `library/planned/simple-systems` are stubs that
  overlap and were never started. Decide: fold, cut, or activate.

## Lab

- **Name the permanent Enhancers shelf** once Open Brain (the first production enhancer) completes; until
  then enhancers live in `extra-credit/` (`experiments/` → `production/`).
