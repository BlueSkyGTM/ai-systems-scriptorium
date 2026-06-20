# Backlog — proposed changes (post-build)

Collected 2026-06-19. Mirrors the live task tracker (ids there don't persist; this file does).

## RESOLVED (2026-06-19, design-polish pass) — caps + positioning
- **Caps consistency:** DONE — sentence case everywhere (H1 + H2/H3 + ToC), codified as STYLE §9; swept 70
  titles + 60 ToC labels (`build-log/caps-sweep.py`). `mdbook build` + `route-lint` PASS.
- **Positioning:** DONE — retitled **"Sans Python — Production AI Engineering"** (lead with the searchable AI
  Engineer role); the AI-Platform-Engineer thesis prose kept verbatim inside preface/conclusion/lessons.
- **Bookmark:** DECLINED (Ray) — no native mdBook bookmark; search is the nav; artifact-scan is the progress.

## RESOLVED (2026-06-19) — 10 of 12 done; 2 are Ray's external actions
- **#1, #2 (design):** DONE — button centered; `theme/syntax-polish.css` (Ayu-magic palette + Rust-light bump + code-card). Pending Ray's visual review.
- **#3 (learner CLAUDE.md):** DONE — `library/completed/sans-python/exercises/CLAUDE.md`.
- **#4 (git-repository-url):** DECIDED — left unset (private-first; 404s for visitors). Set at `GATE-PUBLISH`.
- **#5 (Vercel deploy):** RAY'S ACTION — `vercel.json` ready + path-fixed; needs the dashboard import + subdomain. Can't be done for him.
- **#6 (browser click-test):** RAY'S ACTION — book served + button assets verified (HTTP 200); the actual click is his to make.
- **#7 (73% RAG stat):** DONE — attributed as a soft industry estimate across M2 `03-rag-system` + M5 L11.
- **#8 (banned frame):** DONE — M3 typing exercise "Why" line rewritten to a concrete seam line.
- **#9 (M1/M2 READMEs):** DONE — M1 README fixed (it omitted lessons); M2 was already accurate.
- **#10 (conclusion):** DONE — `src/conclusion.md` send-off + SUMMARY entry.
- **#11 (antilibrary close):** DONE — closing section ties back to the thesis.
- **#12 (platform/course split):** DONE — the restructure (platform/library/ingredients + progression spec); private-first supersedes the public-course framing below.

The original collected items (kept as the record):

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

## Content gaps (from the live review)
10. **Write the book's conclusion / send-off** — the course ends at M8 then the Antilibrary, with no closing
    chapter. Land the journey (thesis full circle, what you've built, the send-off).
11. **Strengthen the antilibrary's closing** — it ends flatly on the Avec Python candidates list; tie it back
    to the thesis (discernment is zero-risk; there's always more to learn).

## Architecture / publishing (decision — "not the final resting place")
12. **Separate the course (public) from the build platform; define the learner-progress convention.** This repo
    tangles three things: the publishable **course** (`src/` + `exercises/` + `theme/` + `book.toml`), the
    reusable **build platform** (`build-stages/` pipeline + `synthesis/` ingredients + `_dossier/` +
    STYLE/AUTHORING — capable of producing/maintaining other books), and **learner progress** (future). Decide:
    a public course repo (Vercel-hosted, learner-forkable) extracted from a private build repo; and where a
    learner's exercise-work is saved so it stays off the public main (fork model / gitignored `work/` /
    separate progress repo). Strategic decision, not a code task yet.

    **Proposed 3-home model (recorded, not decided):** (a) *Private build repo* — this one, tidied: the platform
    + `synthesis/` ingredients + build ledgers; where the build runs and its history lives. (b) *Public course
    repo* — extracted: `src/` + `exercises/` (starters) + `theme/` + `book.toml` + a learner README;
    Vercel-hosted, learner-clonable; the SHIP stage (generalized) publishes into it. (c) *Learner progress = a
    fork* — learners commit exercise-work to their own fork; Ray keeps his learner-work in a personal fork /
    private progress repo, off the public main. Boundaries are already clean, so the extraction is mechanical;
    renaming follows from the split.

> Also still noted in `build-progress.md` (long-standing, not re-raised here): M1 reconciliation + deeper
> ICM-phase formalization. Pull into this backlog if/when they become active.
