# Build Tooling Inventory — `scripts/`

> Source: `scripts/`. These are the repo's lesson-authoring and audit tools — candidate Claude Code tools for extraction/maintenance.

## `_lib.py`

- **Purpose:** Provides shared helper functions for the other scripts in the directory. Currently implements a minimal, dependency-free YAML-subset parser for markdown frontmatter.
- **Produces:** Parsed frontmatter as a dictionary of key-value pairs (returned to the calling script).
- **Run as:** Imported as a module by other scripts (e.g., `from _lib import parse_frontmatter`).

## `audit_lessons.py`

- **Purpose:** Validates structural invariants and conventions across every lesson directory in the `phases/` folder.
- **Produces:** A report detailing any structural issues (missing files, bad directory naming, invalid quiz schemas, unresolvable internal markdown links). Outputs either to stdout as a human-readable text report or to stdout as a JSON payload. Returns an exit code of 1 if issues are found.
- **Run as:** `python scripts/audit_lessons.py [--phase N] [--json] [--strict]`

## `build_catalog.py`

- **Purpose:** Walks the entire curriculum directory structure and compiles a machine-readable inventory of all phases, lessons, source files, and output artifacts.
- **Produces:** A JSON document (`catalog.json` at the repo root by default) containing the curriculum schema, totals, and artifact metadata. Can alternatively output the JSON payload directly to stdout.
- **Run as:** `python3 scripts/build_catalog.py [--out path/to/catalog.json] [--stdout]`

## `check_readme_counts.py`

- **Purpose:** Compares hardcoded numerical counts in `README.md` against the authoritative totals found in `catalog.json` to detect drift.
- **Produces:** A mismatch report to stdout (text or JSON). Can optionally mutate and rewrite `README.md` with the corrected numbers if the `--fix` flag is provided.
- **Run as:** `python3 scripts/check_readme_counts.py [--json] [--fix]`

## `install_skills.py`

- **Purpose:** Discovers, filters, and installs curriculum output artifacts (skills, prompts, agents) into a specified target directory using a chosen file layout.
- **Produces:** Copies artifact markdown files to the target directory and generates a `manifest.json` file logging the copied inventory. Can restrict output to a `manifest.json` without copying files if run with `--dry-run`.
- **Run as:** `python3 scripts/install_skills.py <target_dir> [--type {skill,prompt,agent,all}] [--phase N] [--tag TAG] [--layout {flat,by-phase,skills}] [--dry-run] [--force] [--json]`

## `lesson_run.py`

- **Purpose:** Runs smoke checks against lesson code. By default, it byte-compiles Python files to check for syntax errors. If invoked with `--execute`, it actually runs the lesson's entry script.
- **Produces:** Reports the status (passed, failed, skipped) of each lesson's code to stdout as text or JSON.
- **Run as:** `python3 scripts/lesson_run.py [--phase N] [--strict] [--json] [--execute]`

## `link_check.py`

- **Purpose:** Validates external HTTP and HTTPS links inside all markdown files across the repository.
- **Produces:** A broken link report sent to stdout or stderr (text or JSON). Mutates or creates a hidden cache file (`.link-cache.json`) at the repository root to store validation results.
- **Run as:** `python3 scripts/link_check.py [--phase N] [--path PATH] [--strict] [--json] [--cache DAYS] [--timeout SEC] [--concurrency THREADS]`

## `scaffold-lesson.sh`

- **Purpose:** Generates the boilerplate directory structure and template files for a new curriculum lesson.
- **Produces:** Creates a new lesson directory containing `code/`, `notebook/`, `docs/`, and `outputs/` subdirectories. Populates `docs/en.md` with a lesson template and `code/main.py` with a basic Python skeleton.
- **Run as:** `scripts/scaffold-lesson.sh <phase-dir> <lesson-slug> [title]`

## `scaffold_workbench.py`

- **Purpose:** Installs the "Agent Workbench" pack (contracts, schemas, and helper scripts) into a target project directory to set up an AI builder agent environment.
- **Produces:** Copies the `AGENTS.md` contract, docs, JSON schemas, and helper scripts into the target directory. Seeds `task_board.json` and `agent_state.json` if they do not already exist, and writes a `.workbench-version` pin file.
- **Run as:** `python3 scripts/scaffold_workbench.py <target_dir> [--force] [--minimal] [--dry-run] [--no-seed]`
