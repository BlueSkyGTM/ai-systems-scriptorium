# GLM Extractor — made-with-ml

Repo-specific extractor for the **Made-With-ML** MLOps project. Self-contained: this folder is the skill. (A sibling skill exists in `ai-engineering-from-scratch/` but that one is built for lesson-folder fan-out — wrong shape for this repo. Do not reuse it here.)

**Operating principle:** Claude orchestrates, GLM writes. Claude gathers source blobs and runs the script; GLM does all summarization. Extract the **MLOps concepts and workflow**, not Python syntax (per CONTEXT.md repo notes).

---

## 1. Why this skill is different from the lesson-phase one

| | ai-engineering-from-scratch | **made-with-ml (this)** |
|---|---|---|
| Source shape | ~260 lesson folders, each `docs/en.md` | A Python project: 10 modules, 1 big notebook, deploy configs, Makefile |
| Pattern | `phase` fan-out (1 concurrent call per lesson) | **`single`** (gather a blob → 1 GLM call → 1 doc) |
| Concurrency | 6 workers + throttle (RPM `1302` risk) | Sequential single calls — no concurrency to manage |
| Special tool | — | **`nb-outline`** — parse the 2.5 MB notebook to headings + first-cell snippets (never full cells) |

So the runner here (`extract.py`) has **two modes only: `single` and `nb-outline`.** No phase mode.

---

## 2. API config (universal — same key/plan across repos)

- **Model:** `glm-5.1` (preferred). Override via `GLM_MODEL`.
- **Endpoint:** `https://api.z.ai/api/coding/paas/v4/chat/completions` (OpenAI-compatible).
- **Key:** `3ee9e7dff7ca48199128ee2d70e7591d.dQf6EjZtSElYB1vc` — a **coding-plan** key. **No second keys.**

### Two traps that are NOT repo-specific (they're the key/plan reality)
1. **`1113` "insufficient balance" on a general endpoint = model-not-in-plan, not an empty wallet.** This coding-plan key only works on `/api/coding/`. (Even `glm-4.6` `1113`s on the general endpoint.) `glm-4-plus` & the high-concurrency roster live on the general platform — unreachable with this key.
2. **glm-5.x are reasoning models → thinking OFF.** Without `"thinking":{"type":"disabled"}` they spend the whole `max_tokens` on reasoning and return **empty** content. `extract.py` sends it on every call. (An empty completion is retried and the error hints "is thinking disabled?".)

Rate limit `1302` only bites under concurrency; single-mode here won't hit it. `call_glm` still retries 8× with longer backoff on `1302`, just in case.

---

## 3. `extract.py` — the runner

```bash
# single: one GLM call from a source blob you build
python3 skills/glm-extractor/extract.py single \
  --user-file BLOB.txt --out output/<FILE>.md [--max-tokens 3000] [--system-file SYS.txt]

# nb-outline: mechanical, no GLM. headings + first-cell snippet per section.
python3 skills/glm-extractor/extract.py nb-outline \
  --ipynb notebooks/madewithml.ipynb --out /tmp/nb_outline.txt [--max-snippet 500]
```
Defaults: `MODEL=glm-5.1`, thinking disabled, `temperature 0.3`, 8 retries. Default system prompt is MLOps-flavored (concepts over syntax); override with `--system-file` if a target needs different framing.

**The work is in building the blob.** For each target, Claude assembles a `BLOB.txt` = an instruction (from the CONTEXT.md target spec) + the gathered source (dir listings, module heads, the notebook outline, deploy file contents, the Makefile). Then one `single` call.

---

## 4. Targets → how to source each (this repo)

| Target | Output | How to gather the blob |
|---|---|---|
| 1 · Repo inventory | `output/inventory.md` | `find`/`ls` trees of root, `madewithml/`, `notebooks/`, `deploy/`, `datasets/`, `tests/` + 1-line file purposes. GLM writes the tree-with-purposes. |
| 2 · Notebook outline | `output/content/module4-madewithml-notebook-outline.md` | `nb-outline` on `notebooks/madewithml.ipynb` → outline blob; GLM adds 1–2 sentence summaries and tags **MLOps** (serving/monitoring/deploy) vs **training** sections. |
| 3 · Code inventory | `output/content/module4-madewithml-code-inventory.md` | Concatenate each `madewithml/*.py` (modules have **no docstrings** — GLM infers purpose from imports + defs). GLM emits a table: module \| purpose \| seam (serving/training/eval/infra). |
| 4 · Deploy scripts | `output/content/module4-deploy-scripts.md` | Dump every file under `deploy/`. GLM table: file \| purpose \| infra target \| student build task. |
| 5 · Makefile | append to code-inventory | `Makefile` (targets: `style`, `clean`). GLM table: target \| command \| purpose. Append as a `## Makefile` section. |
| 6 · Visuals | `output/visuals/` | **None in this repo** (no png/svg/jpg, no mermaid). Log "no visuals found" in inventory.md. Mechanical — no GLM. |
| — Curriculum map | `output/curriculum-map.md` | Derived: map repo sections → Module 4 (MLOps in practice / data versioning / serving). One `single` call. |
| — Antilibrary | `output/antilibrary.md` | Note the training-internals modules (`train.py`, `tune.py`, `models.py`) as out-of-seam (the seam is serving/MLOps, not model training). One `single` call. |

---

## 5. Verification protocol — never trust "done"

After each target: open the file, check it's non-empty and covers every source item (e.g. all 10 modules in the code inventory, all 6 deploy files, both Makefile targets, all 36 notebook headings). Grep the source folder counts and compare. Only then check the CONTEXT.md Done Checklist — with the verified count, not a bare `[x]`. (Prior sessions stubbed empty files and marked them done; don't.)

---

## 6. File manifest

```
skills/glm-extractor/
├── SKILL.md      ← this spec (made-with-ml)
└── extract.py    ← runner: single | nb-outline
```
