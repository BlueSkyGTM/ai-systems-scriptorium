# CONTEXT — build-log/ (the build journal + per-book ledgers)

The record of how each book was built: PLANs, verify/build-test/ship verdicts, and the running build
journal. These are **records**, not active workspaces — you read them, you don't route work into them.

## What's here

- `sans-python/` — the shipped book's ledgers: `build-progress.md`, the per-module
  `mN/{PLAN.md, output/{author,verify,ship}/}`, plus the midway/coverage reviews.
- `restructure-spec.md` — the spec + autoplan review for the repo restructure.

## When to read it

- **Fixing a shipped lesson** → read that module's `build-log/sans-python/mN/output/verify/` verdict
  to see what was checked and not regress it. That's the one live reason to open this folder.
- Historical context on a decision.

## Don't

- Don't author here; author against `ingredients` via `platform/pipeline`.
- These ledgers are **records**: their historical paths (`northstar/migration`, `synthesis/source`)
  are left as written and are exempt from `route-lint`. Do not "fix" them.

No gates own this folder.
