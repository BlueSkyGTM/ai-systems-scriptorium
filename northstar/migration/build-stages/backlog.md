# Backlog — proposed changes (post-build)

Collected 2026-06-19 (the course itself is complete: all 8 modules shipped, `mdbook build` PASS). These are
proposed changes from Ray's design review + the deferred polish — **not yet implemented; collected for tracking.**
Mirrors the live task tracker (task ids there don't persist across sessions; this file does).

## Design (from the live book review — hold, don't implement yet)
1. **Center the "Copy for Claude Code" button** — `theme/copy-to-claude.css`; the `.claude-handoff-btn` is
   currently left/inline, center it.
2. **Deepen code-block contrast & color** — richer syntax color and more contrast, toward the real VS Code
   Rust theme; "deepen it until it catches that Ayu magic." Reference: the glium docs.rs screenshot Ray shared.
   Likely a `theme/` highlight override or a custom syntax theme.

## Features / config
3. **Learner-facing `CLAUDE.md` in `exercises/`** — so Claude Code opens each exercise in "guide the student,
   don't dump the answer" mode (read the lesson + exercise README; the artifact extends the module throughline;
   coach, don't complete). Distinct from the authoring `CLAUDE.md`.
4. **Set `book.toml` `git-repository-url`** → `https://github.com/BlueSkyGTM/sans-python` (adds a repo link in
   the book header) — **only if the repo is public** (else it 404s for visitors). Confirm visibility first.

## Deploy / QA
5. **Deploy the book to the Vercel subdomain** — `vercel.json` is pushed (Vercel-builds strategy, validated
   locally). Remaining (Ray's Vercel dashboard): import `BlueSkyGTM/sans-python`, build, move the subdomain
   onto it, retire the old "lost its meaning" project, verify. *(Ray set this aside for now.)*
6. **Live in-browser button smoke test** — local serve is up; assets + handoff div load (HTTP 200, hashed
   assets serve). Remaining: click the button in a browser and confirm it copies the payload (needs a secure
   context — https/localhost). Closes earlier item (a).

## Closing-pass polish (the original deferred backlog, item c)
7. **Reconcile the ~73% RAG-retrieval-failure stat** across M2 `03-rag-system.md` + M5 lesson 11 — soft
   provenance; rule on attribution/hedge across both together.
8. **Fix the banned "An AI Platform Engineer who…" frame** in `exercises/module3/05-typing-the-product-layer/README.md`.
9. **Re-read M1/M2 module Overview READMEs** against the final shipped structure.

> Also still noted in `build-progress.md` (long-standing, not re-raised here): M1 reconciliation + deeper
> ICM-phase formalization. Pull into this backlog if/when they become active.
