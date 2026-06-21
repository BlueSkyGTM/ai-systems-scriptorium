# Provenance — NumPy user guide (ore)

A curated subtree, not a full-repo clone; tactical, just the teachable arc.

- Source: https://github.com/numpy/numpy , the `doc/source/user/` user guide.
- Commit: `706b103`. Pulled 2026-06-20.
- License: BSD-3-Clause (see `LICENSE.txt`). Distillable; derivatives permitted.
- Trim: dropped `absolute_beginners.rst` (redundant beginner scaffold) and the `c-info.*`
  C-extension-author cluster (off-target for an applied-Python book). Kept the NumPy /
  vectorization arc: quickstart, broadcasting, indexing, copies-vs-views, ufuncs, dtypes,
  io, structured arrays, performant code, the how-to set.
- Feeds: the planned **Only Python** book. Reference-grade rST: accurate mechanics and
  examples; the teaching narrative is added at authoring (the ore is the raw material).
- Recoverable: re-pull `doc/source/user/` from the source repo at the commit above.
