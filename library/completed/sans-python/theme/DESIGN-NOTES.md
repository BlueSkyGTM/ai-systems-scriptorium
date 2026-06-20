# Front-end design decisions — Sans Python

The living record of the book's front-end choices, so a future theme-touch doesn't re-litigate them.
Keep this current whenever a front-end choice changes.

## Theme

- **mdBook themes:** `default-theme = "rust"` (warm light), `preferred-dark-theme = "ayu"` (deep, saturated
  dark). Chosen for a distinctive, readable look that isn't generic-doc-site grey.
- **`theme/syntax-polish.css`** deepens code blocks toward the real VS Code Rust look and the Ayu palette:
  a deeper-than-page canvas so blocks pop, saturated high-contrast tokens (orange keywords, lime strings,
  gold functions, blue types, purple numbers, italic comments), and a code-as-card container (rounded,
  padding, a thin per-theme border). Scoped per theme class (`.ayu` vs `.rust`/`.light`).
- **Code-block edge + scrollbar fix (2026-06-20).** `pre > code` now uses `box-sizing: border-box`, which
  removes a spurious horizontal scrollbar that showed on every block: as `content-box` the left/right padding
  pushed the border-box wider than the parent, tripping `overflow-x: auto` even with nothing to scroll. The
  faint universal inset ring became a real thin border, tinted per theme so a block separates from the
  near-same-color page: orange (`rgba(255,143,64,0.30)`) in Ayu, faint rust (`rgba(165,49,15,0.16)`) in
  light/Rust.

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
