# CONTEXT — vault/ (THE ORE — raw source repos)

The nine raw source repositories the books are distilled from. ~767M, on local disk only. This is the
**ore**, not authoring input: you do not write lessons from here directly. You distill ore into
`ingredients/` first, then author against `ingredients/`.

The vault is **gitignored** (manifest-primary, recoverable). Only this `CONTEXT.md` and `MANIFEST.md`
are committed (via `.gitignore` negations); the raw repos are not versioned here.

## What's here

`MANIFEST.md` — the nine repos: name, what each feeds, clone URL where discoverable, and the
recoverable-on-disk note. See it for the inventory and provenance.

## Process-ore route

1. Pick the planned book and its named ore (see the book's `CONTEXT.md` and `vault/MANIFEST.md`).
2. Distill the relevant `vault/<repo>/` into `ingredients/source/` + a `ingredients/dossiers/`
   ruling.
3. Author against `ingredients` via `platform/pipeline/CONTEXT.md`.

## Load / don't-load

- **Load:** `vault/MANIFEST.md`, then only the specific `vault/<repo>/` you are distilling.
- **Do NOT load:** the whole vault (huge), shipped books, the pipeline internals until you've
  distilled into `ingredients`.

## Gates

Starting a new book from ore: `GATE-NAME-BOOK` then `GATE-LOCK-PLAN` (see `platform/HUMAN-GATES.md`).

> route-lint note: `vault/**` is route-excluded — its files are not scanned for links, and no live
> route may target it.
