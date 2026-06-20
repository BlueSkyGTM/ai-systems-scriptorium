# Antilibrary gap report — ranked by hireability (2026-06-19)

What *Sans Python* deliberately cut, ranked against the 2026 hiring screens (% of postings) from
[`hireability-alignment.md`](hireability-alignment.md). Source of the cuts: [`../../library/completed/sans-python/src/antilibrary.md`](../../library/completed/sans-python/src/antilibrary.md)
and the scope rationale in [`roadmap-coverage.md`](roadmap-coverage.md). Also a GBrain node: `antilibrary-gap-report`.

The point of the report: a cut is not a loss, it is a deferral with a pointer. This ranks the deferrals
by how much they actually cost the [`hireability-alignment.md`](hireability-alignment.md) goal.

## Ranked gaps

| # | Cut material | Hiring screen | Status in the course | Gap risk |
|---|---|---|---|---|
| 1 | **Advanced Python** (NumPy/Pandas/vectorization) | **94%** | Point-of-use only — the "Sans Python" bet opts out by design | 🔴 Highest |
| 2 | **PyTorch/TF + model training** | **78%** | Thin LoRA/fine-tune *literacy* (M5 L13); no training builds | 🔴 High |
| 3 | **Classic ML** (regression/trees/boosting, AUC-ROC, feature-eng) | part of ML-sys-design 48% | Skipped (GenAI specialization) | 🟠 Medium |
| 4 | **Data eng / SQL** (Kafka/Spark/Airflow/warehouses/lineage) | **52%** | Only the Docling ingestion front-door (M5 L11) | 🟠 Medium |
| 5 | **MLOps infra** (IaC/Terraform, DVC, deep exp-tracking) | part of MLOps 63% | MLflow literacy (M5 L12); rest cut | 🟡 Med-low |
| 6 | **ML math depth** (linear algebra/calculus/probability) | Step 2 | Conceptual only (M1) | 🟡 Low (applied) |
| 7 | Generative media (GANs/diffusion/image/video) | — | Cut (~90% off-seam) | ⚪ Very low |
| 8 | Frontier-safety research & policy (STaR/RSP/METR) | — | Cut (researcher track) | ⚪ Very low |
| 9 | Model-from-scratch + distributed training | — | Cut (M6–M8; MLE/research) | ⚪ Low |
| 10 | Pre-transformer NLP (word2vec/RNN/seq2seq) | — | Cut at the attention seam (M1) | ⚪ Very low |
| 11 | Edge AI (Jetson/TFLite), Go | — | Cut (niche for target) | ⚪ Very low |

## The read

- **The single biggest gap is #1, advanced Python** (94% screen) — and it's literally the thing the
  book's name opts out of. **#2 PyTorch** is close behind.
- **Rows 7–11 are *correctly* cut** — they don't block the AI-Engineer target, and chasing them would
  weaken the fork (the [`roadmap-coverage.md`](roadmap-coverage.md) MLE-splinter decision).
- **Rows 1, 2, 3, 6 are the real exposure** — and they are now the spine of the **focused planned books**
  (the retired "Avec Python" umbrella, split): row 1 → **Just Python**; rows 2/3/6 → **Machine Learning**
  (applied/literacy depth). Not a problem to patch in *this* book — the outline of the next ones.
- **Rows 4–5 are the only place a small literacy touch in *this* book might still pay off** (a data-eng /
  SQL nod beyond the Docling front-door).

## Next move

The gaps map to **focused books, not a backfill**. The "Avec Python" umbrella is retired; the rows split
into planned books under `library/planned/`: row 1 → **Just Python**, rows 2/3/6 → **Machine Learning**,
row 4 → **Data Engineering**. Rows 5 and 7–11 stay light or cut. Nothing here is a deficit — it is the
next move, already located.
