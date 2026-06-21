# Color Palettes — One Signature per Book

Color is a learning aid: each Scriptorium book carries one signature accent the reader
associates with it, the way Sans Python is rust. The set shares rust's qualities (muted,
warm-readable, never neon) and spreads around the wheel so the books stay distinct but
harmonious. Approved by Ray on 2026-06-20.

Each book gets a LIGHT accent (warm paper / Rust theme) and an AYU-DARK accent (deeper
canvas, brighter accent), exactly as Sans Python pairs rust `#b7410e` (light) with `#ff8f40`
(Ayu). The dark values below are starting points; tune them at build the way the rust theme
was tuned.

| Book (working title) | Dir | Light accent | Ayu-dark accent | Note |
|---|---|---|---|---|
| Sans Python | `completed/sans-python` | `#b7410e` | `#ff8f40` | shipped anchor (rust) |
| Only Python | `planned/just-python` | `#b8860b` | `#e6b800` | goldenrod; a quiet Python-yellow nod |
| Machine Math | `planned/ml-in-proportion` | `#4b3f9e` | `#9a8cff` | indigo; abstract, mathematical |
| Data Currents | `planned/upstream` | `#0f7d72` | `#2dd4bf` | teal; water and flow |
| Weights and Measures | `planned/tasteful-tuning` | `#9e2b3a` | `#ff6b81` | crimson; the gravity of training |
| Algorithmic Interviewing | `planned/interview-algorithm` | `#2f6b4f` | `#5fd39a` | pine; calm and confident (title still settling) |
| Local Metal | `planned/local-metal` | `#3a6ea5` | `#5fa8e6` | steel blue; cool hardware |

## How Each Palette Is Applied (per Book Theme, at Build)

Mirror the Sans Python theme pattern (`theme/copy-to-claude.css` + `theme/syntax-polish.css`):

- the Claude Code handoff frame is the one loud accent on the page;
- heading and link accents pick up the signature hue;
- the code-block edge stays a quiet neutral, since the accent is reserved for the handoff and
  inline emphasis (the hierarchy Sans Python settled: prose base, quiet code cards, one loud accent).

Light variants sit on warm paper; Ayu-dark variants sit on a deeper-than-page canvas. The point
is recognition: a reader should know which book they are in from the color alone.
