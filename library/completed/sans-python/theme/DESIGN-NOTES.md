# Front-end design decisions — Sans Python

The living record of the book's front-end choices, so a future theme-touch doesn't re-litigate them.
Keep this current whenever a front-end choice changes.

## Theme

- **mdBook themes:** `default-theme = "rust"` (warm light), `preferred-dark-theme = "ayu"` (deep, saturated
  dark). Chosen for a distinctive, readable look that isn't generic-doc-site grey.
- **`theme/syntax-polish.css`** deepens code blocks toward the real VS Code Rust look and the Ayu palette:
  a deeper-than-page canvas so blocks pop, saturated high-contrast tokens (orange keywords, lime strings,
  gold functions, blue types, purple numbers, italic comments), and a code-as-card container (rounded,
  inset border, padding). Scoped per theme class (`.ayu` vs `.rust`/`.light`).

## The Claude Code handoff block (`theme/copy-to-claude.{css,js}`)

- Each exercise lesson ends with a **rust-accented box** (left border + warm tint) carrying a one-line,
  **per-exercise** description and a **"Copy for Claude Code"** button. The button copies a structured
  payload (course, lesson, lesson file, exercise path, task) for pasting into Claude Code.
- **Button:** centered, fit-content, rust in light/Rust theme (`#b7410e`), Ayu-orange with dark text in
  dark themes (`#ff8f40`), green "Copied ✓" confirm. Sized for comfortable padding (not cramped).
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
