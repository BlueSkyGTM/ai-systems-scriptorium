# Front-end design decisions — Sans Python

The living record of the book's front-end choices, so a future theme-touch doesn't re-litigate them.
Keep this current whenever a front-end choice changes.

**Status (2026-06-20): design locked.** Ray approved the full theme — the rust/Ayu palette, the
code-as-card blocks with quiet neutral edges, the rust handoff CTA, and the near-white Ayu reading
text. Treat the choices below as settled; do not re-open them without a new directive. This is also the
reference theme the other books in the lineup inherit (see `platform/conventions/PALETTES.md`).

## Theme

- **mdBook themes:** `default-theme = "rust"` (warm light), `preferred-dark-theme = "ayu"` (deep, saturated
  dark). Chosen for a distinctive, readable look that isn't generic-doc-site grey.
- **`theme/syntax-polish.css`** deepens code blocks toward the real VS Code Rust look and the Ayu palette:
  a deeper-than-page canvas so blocks pop, saturated high-contrast tokens (orange keywords, lime strings,
  gold functions, blue types, purple numbers, italic comments), and a code-as-card container (rounded,
  padding, a thin per-theme border). Scoped per theme class (`.ayu` vs `.rust`/`.light`).
- **`theme/readability.css` — dark-theme reading foreground (2026-06-20).** mdBook's stock Ayu `--fg`
  is `#c5c5c5`, a muted gray that reads as "transparent" over a long session. It is lifted to a crisp
  near-white (`#ededed`), matched to the Claude Code desktop UI, so the reading text is easy on the eyes.
  Only the plain prose/heading foreground changes: the rust accent, the inline-code gold, and the syntax
  tokens are set explicitly in `syntax-polish.css` and do not read from `--fg`. The Rust / light theme is
  left at near-black on warm paper (its issue would be the opposite of transparent). This is the standard
  every book's dark theme should inherit; see `platform/conventions/PALETTES.md`.
- **Code-block edge + scrollbar fix (2026-06-20).** `pre > code` now uses `box-sizing: border-box`, which
  removes a spurious horizontal scrollbar that showed on every block: as `content-box` the left/right padding
  pushed the border-box wider than the parent, tripping `overflow-x: auto` even with nothing to scroll. The
  faint universal inset ring became a real thin border, kept **neutral and quiet** so a code block reads as a
  recessed container and the accent stays reserved for syntax tokens, inline code, and the handoff CTA: a faint
  warm-gray edge per theme (light `rgba(190,188,182,0.16)` on Ayu's dark canvas, taupe `rgba(120,113,100,0.18)`
  on the light paper). A first pass used an accent-orange edge (`rgba(255,143,64,0.30)`); it made every block
  wear the accent and flattened the page hierarchy, so it was dialled back.
- **Border visibility raised, kept neutral (2026-06-20).** The dialled-back alpha (`0.16`/`0.18`) read as
  reliably present on the Ayu dark theme but fell below the perceptual threshold on the light/Rust theme:
  syntax-colored blocks looked edged while plain blocks (a no-language block, a shell one-liner) looked
  border-less, so the page seemed to have borders on some blocks and not others. The edge is on every
  `pre > code` (it never was truly missing); the neutral alpha was raised to a clearly visible but quiet
  level. The semi-transparent values still read too faint on the Ayu dark theme, where the code canvas
  sits a hair off the page, so the edge is now a solid neutral color and every block reads as a clear card:
  Ayu `#3a424e`, light `#c7baa1`. Still neutral, not the accent, which stays reserved for the handoff CTA,
  inline code, and syntax tokens.

## The Claude Code handoff block (`theme/copy-to-claude.{css,js}`)

- Each exercise lesson ends with a **rust-accented box** (uniform rust frame + warm tint) carrying a one-line,
  **per-exercise** description and a **"Copy for Claude Code"** button. The button copies a structured
  payload (course, lesson, lesson file, exercise path, task) for pasting into Claude Code.
- **Uniform border (2026-06-20).** The box had a 4px rust `border-left` plus a 1px border on the other three
  sides; the mismatch read as inconsistent. It is now a single uniform `4px` frame on all sides (rust
  `#b7410e` in light/Rust, Ayu-orange `#ff8f40` in dark): the left-border weight, applied all around.
- **Button:** centered, fit-content, rust in light/Rust theme (`#b7410e`), Ayu-orange with dark text in
  dark themes (`#ff8f40`), green "Copied ✓" confirm. Sized for comfortable padding (not cramped).
- **Button text size = `font-size: inherit` (2026-06-20).** It now matches the exercise description (the
  body reading size). It was pinned at `0.98rem`, which under mdBook's 62.5% root is ~9.8px against the
  16px description; that size contrast was jarring next to the description it sits under. Weight stays 600
  (it is still a CTA); only the size was unshrunk.
- **No "Exercise · path" tag (removed 2026-06-20).** It was Claude-facing info shown to the reader, too
  small, and redundant once every description became unique. The `data-exercise` attribute and the
  payload's `Exercise:` line stay — that's the part Claude needs; the reader doesn't.
- **Descriptions are unique per exercise** and start capitalized (verb chosen by type: Build It / Inspect
  It / Try It in Claude Code).

## Prose & headings (also in `platform/conventions/STYLE.md`)

- **Headings: Title Case** — every major word capitalized, minor words (articles, short conjunctions/
  prepositions) lowercased except first/last; acronyms/proper nouns preserved. Sweep:
  `build-log/caps-sweep-title.py`. (STYLE §9.)
- **No em-dashes** — they read as an AI tell. Semicolon to join clauses, colon to introduce (and for the
  handoff CTA + module-divider titles), commas for a parenthetical aside. Sweep:
  `build-log/em-dash-sweep.py`. (STYLE §2.) Em-dashes left only in tables (placeholders) and code.

## Avoid AI tells generally

The book is a hireability artifact; it must not read as machine-generated. Beyond em-dashes, watch for
the usual tells (the "it's not just X, it's Y" cadence, hedging filler, uniform paragraph shapes) — STYLE
§8 (variety) is the backstop.
