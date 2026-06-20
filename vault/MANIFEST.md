# vault MANIFEST — the nine source repos

The ore the Scriptorium distills into books. ~767M total, on local disk only, **gitignored**
(manifest-primary). Each repo is **recoverable; on disk only** — re-clone from the URL below if lost.
Module feeds are from `ingredients/source/INDEX.md` (the librarian's inventory of what each repo fed).

| Repo (`vault/…`) | Prefix | Size | Feeds (modules) | Clone URL |
|---|---|---|---|---|
| `ai-engineering-from-scratch` | `aefs` | 22M | M1, M2, M3, M4, M5 (the spine source) | https://github.com/rohitg00/ai-engineering-from-scratch |
| `ai-performance-engineering` | `aipe` | 725M | M4 (deploy/serving/perf) | not discoverable (README points to a `your-username` placeholder); recoverable on disk |
| `ai-system-design-guide` | `asdg` | 2.8M | M2, M3, M4; primary ore for the planned *Simple Systems* + *Getting Hired* books | https://github.com/ombharatiya/ai-system-design-guide |
| `fleet-engineering` | `fleet` | 1.2M | M3 (fleet patterns/reference/schemas) | https://github.com/cobusgreyling/fleet-engineering |
| `loop-engineering` | `loop` | 2.6M | M3 (loop patterns) | https://github.com/cobusgreyling/loop-engineering |
| `loop-engineering-orange-book` | `obook` | 7.2M | loop/agent reference (supporting) | https://github.com/alchaincyf/loop-engineering-orange-book |
| `made-with-ml` | `mwml` | 3.2M | M4 (design·develop·deploy·iterate) | https://github.com/GokuMohandas/Made-With-ML |
| `typescript-projects` | `ts` | 1.8M | M1, M3 (TS threaded in) | https://github.com/LearningTypeScript/projects |
| `100-exercises-to-learn-rust` | `rust` | 2.3M | M1, M5 (Rust threaded in) | https://github.com/mainmatter/100-exercises-to-learn-rust |

## Notes

- **`ai-performance-engineering` (725M)** is the bulk of the vault; its top-level README has no real
  origin URL (placeholder `github.com/your-username/...`). It carries a large binary
  (`resources/NVIDIA_GTC_2026_...pdf`). Treat it as on-disk-only until a real source is confirmed.
- **Recoverable:** the vault was never committed; it is the ore's only on-disk copy. If you need a
  durable backup, back it up out-of-band — git is not backing it up.
- **Provenance for distilled content** lives in `ingredients/source/_repos/<repo>/` (per-repo
  inventory, curriculum-map, antilibrary, visuals) and `ingredients/source/INDEX.md`.
