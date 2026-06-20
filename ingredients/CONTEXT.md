# CONTEXT — ingredients/ (distilled inputs)

The in-git, small, distilled inputs the pipeline authors against. This is what you load to write a
lesson — **not** the `vault` raw ore.

## What's here

- `source/` — the consolidated, crawlable per-module distilled source (the librarian's inventory;
  `source/INDEX.md` lists everything, `source/_repos/` holds per-repo metadata).
- `dossiers/` — the keep/cut/merge/thread rulings per module: what belongs in a lesson and why.

## Load / don't-load

- **Load:** the module's `dossiers/moduleN.md` (the ruling) + the matching `source/moduleN/` files
  (the depth), as the AUTHOR stage directs.
- **Do NOT load:** the `vault` raw ore (this folder is the distilled form of it), shipped books, the
  pipeline internals unless authoring.

## Handoff

Feeds `platform/pipeline/` AUTHOR. Processing new vault ore *into* ingredients starts at
`vault/CONTEXT.md`. No gates own this folder.
