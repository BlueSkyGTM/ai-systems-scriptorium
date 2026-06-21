# The Book Theme — One, Shared (Per-Book Palettes Retired)

> **Executive decision, 2026-06-20:** per-book color signatures are retired. The debugging cost of
> tuning a distinct palette per book outweighed the variety benefit and threatened to stall production.
> **Every book uses the one Scriptorium theme, without exception** — the theme proven on Sans Python.
> Quality over variety.

## The One Theme

Every book copies Sans Python's `theme/` verbatim. `default-theme = "rust"` (warm light),
`preferred-dark-theme = "ayu"` (deep dark). Four files:

- **`copy-to-claude.css` + `copy-to-claude.js`** — the Claude Code handoff block: a uniform
  **Claude-orange** frame and button (`#b7410e` light, `#ff8f40` Ayu) and the "Copy for Claude Code"
  payload button. The **only** per-book change anywhere in the theme is the `COURSE` string in the `.js`
  (the payload's course name); the colors never change.
- **`syntax-polish.css`** — the code-block treatment: a code-as-card container with a clearly visible
  neutral border (Ayu `#3a424e`, light `#c7baa1`), a deeper-than-page canvas, and the saturated
  VS-Code-style syntax palette (Ayu: orange keywords, lime strings, gold functions, blue types, purple
  numbers; light: rust-red keywords, green strings, amber functions, blue types, purple numbers).
- **`readability.css`** — the dark-theme reading foreground (below).

A new book: copy these four files, set the `COURSE` string in the `.js`, list the three CSS files in
`book.toml` `additional-css`. No `palette.css`, no per-book accents. Sans Python is the canonical theme;
its `theme/DESIGN-NOTES.md` is the living record of every theme decision.

## Dark-Theme Reading Foreground

Every book's Ayu dark theme lifts the stock mdBook foreground (`--fg: #c5c5c5`, a muted gray that reads
as "transparent") to a crisp near-white (`#ededed`), matched to the Claude Code desktop UI so long
reading sessions stay easy on the eyes. Shipped as `theme/readability.css` (`.ayu { --fg: #ededed; }`),
loaded after the stock variables. It touches only the plain prose foreground; the syntax-token colors are
unchanged. The light / Rust theme keeps near-black text on warm paper.

## Retired: The Per-Book Signature Table (Historical)

The lineup once planned a distinct accent per book (goldenrod for Just Python, indigo for Machine Math,
teal for Data Currents, crimson for Weights and Measures, pine for Anatomy of an Answer, steel blue for
Local Metal). That approach is retired per the decision above; the colors are recorded here only as
history, not as instructions. Do not implement them.
