# vault MANIFEST — the source ore (nine repos + curated doc subtrees)

The ore the Scriptorium distills into books. ~767M total, **committed to this private repo verbatim**
(2026-06-20; previously gitignored/manifest-primary). Each repo is also recoverable by re-cloning the URL below.
Module feeds are from `ingredients/source/INDEX.md` (the librarian's inventory of what each repo fed).

| Repo (`vault/…`) | Prefix | Size | Feeds (modules) | Clone URL |
|---|---|---|---|---|
| `ai-engineering-from-scratch` | `aefs` | 22M | M1, M2, M3, M4, M5 (the spine source) | https://github.com/rohitg00/ai-engineering-from-scratch |
| `ai-performance-engineering` | `aipe` | 725M | M4 (deploy/serving/perf) | not discoverable (README points to a `your-username` placeholder); recoverable on disk |
| `ai-system-design-guide` | `asdg` | 2.8M | M2, M3, M4; primary ore for the planned *Anatomy of an Answer* (interview) book | https://github.com/ombharatiya/ai-system-design-guide |
| `fleet-engineering` | `fleet` | 1.2M | M3 (fleet patterns/reference/schemas) | https://github.com/cobusgreyling/fleet-engineering |
| `loop-engineering` | `loop` | 2.6M | M3 (loop patterns) | https://github.com/cobusgreyling/loop-engineering |
| `loop-engineering-orange-book` | `obook` | 7.2M | loop/agent reference (supporting) | https://github.com/alchaincyf/loop-engineering-orange-book |
| `made-with-ml` | `mwml` | 3.2M | M4 (design·develop·deploy·iterate) | https://github.com/GokuMohandas/Made-With-ML |
| `typescript-projects` | `ts` | 1.8M | M1, M3 (TS threaded in) | https://github.com/LearningTypeScript/projects |
| `100-exercises-to-learn-rust` | `rust` | 2.3M | M1, M5 (Rust threaded in) | https://github.com/mainmatter/100-exercises-to-learn-rust |
| `numpy-docs` (subtree) | `npdoc` | 2.9M | Just Python (NumPy/vectorization) | github.com/numpy/numpy `doc/source/user/` @706b103, BSD-3 |
| `pandas-docs` (subtree) | `pddoc` | 1.2M | Just Python, Data Currents (Pandas) | github.com/pandas-dev/pandas `doc/source/user_guide/` @c3a779c, BSD-3 |

## Notes

- **`ai-performance-engineering` (725M)** is the bulk of the vault; its top-level README has no real
  origin URL (placeholder `github.com/your-username/...`). It carries a large binary
  (`resources/NVIDIA_GTC_2026_...pdf`). Treat it as on-disk-only until a real source is confirmed.
- **Versioned (2026-06-20):** the vault is now committed to this private repo verbatim (force-added past
  the vendored repos' own .gitignore), so git is the durable backup. The historical "gitignored, on-disk
  only" framing no longer applies.
- **Curated doc subtrees (2026-06-20):** `numpy-docs` and `pandas-docs` are not full-repo clones;
  they are the BSD-3 user-guide trees (`doc/source/user/` and `doc/source/user_guide/`), trimmed to
  the applied arc, pulled as tactical ore for Just Python. Vetted via the tiered-orchestration run
  (one Opus handler, four Sonnet workers). See each folder's `PROVENANCE.md`; recoverable at the pinned
  commit. The PythonDataScienceHandbook was rejected: its prose is CC-BY-NC-ND (no derivatives).
- **Provenance for distilled content** lives in `ingredients/source/_repos/<repo>/` (per-repo
  inventory, curriculum-map, antilibrary, visuals) and `ingredients/source/INDEX.md`.
