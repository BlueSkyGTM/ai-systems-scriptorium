# Front-end Design Decisions: Machine Math

The living record of the book's front-end choices, so a future theme-touch doesn't re-litigate them.

**Status (2026-06-21): theme inherited and locked.** Machine Math uses the shared Scriptorium theme
**verbatim**. The four `theme/` files are byte-identical to Sans Python's; the only per-book change
anywhere is the `COURSE` string in `copy-to-claude.js`. Per-book color signatures were retired by
executive decision (the debugging cost outweighed the variety benefit); every book uses the one theme.
The canonical theme record is Sans Python's `theme/DESIGN-NOTES.md`. See
`platform/conventions/PALETTES.md`. Do not re-open these choices without a new directive.

## What Is Inherited (the whole theme)

- **mdBook themes:** `default-theme = "rust"` (warm light), `preferred-dark-theme = "ayu"` (deep dark).
- **`copy-to-claude.{css,js}`** — the Claude Code handoff block: a uniform Claude-orange frame and button
  (`#b7410e` light, `#ff8f40` Ayu), `font-size: inherit`, green "Copied" confirm. Only the `COURSE` string
  in the `.js` is book-specific.
- **`syntax-polish.css`** — the code-as-card treatment: a clear solid neutral border (Ayu `#3a424e`,
  light `#c7baa1`), a deeper-than-page canvas, the saturated VS-Code syntax palette, and
  `box-sizing: border-box` (kills the spurious horizontal scrollbar).
- **`readability.css`** — the Ayu reading foreground lifted to the all-books near-white `#ededed`.

There is no `palette.css` and no per-book accent.
