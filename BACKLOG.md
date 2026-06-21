# Backlog — open cross-cutting items

Only what is still open. Resolved items live in git history and `build-log/`; they were pruned from here
2026-06-21 to keep the focus on book building.

## Publish-time (gated at `GATE-PUBLISH`; private-first until then)

- **Vercel deploy** — `vercel.json` is ready and locally validated. Remaining is Ray's dashboard work:
  import `BlueSkyGTM/ai-systems-scriptorium`, build, move the subdomain onto it, verify.
- **Set `book.toml` `git-repository-url`** — only when the repo goes public (else it 404s for visitors).

## Strategic (deferred)

- **Bot Bottega** — the engine for building **AI Operating Systems** (Claude-documented systems an AI can
  manage and operate, e.g. the GTM engine), not content mills like ICM. Salvaged from the Scriptorium's
  machinery (gates + orchestration + contract pattern + optional ICM) plus an onboard-for-autonomy,
  fail-fast intake. **Decided 2026-06-21: build it, ship it to its own repo, then scrub it from this repo**
  (it does not belong in the book factory). Next: `/autoplan` the build. See the bot-bottega auto-memory.
- **Stub books** — `library/planned/show-dont-tell` and `library/planned/simple-systems` are stubs that
  overlap and were never started. Decide: fold, cut, or activate.

## Lab

- **Name the permanent Enhancers shelf** once Open Brain (the first production enhancer) completes; until
  then enhancers live in `extra-credit/` (`experiments/` → `production/`).
