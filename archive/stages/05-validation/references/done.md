# Done Protocol

Run this only after the validation report shows all checks passing.

## What This Does

Archives the entire original ICM repo into `.claude/icm-archive/`. The built workspace
stays exactly where it is. Setup then runs inside the workspace and takes over naturally.

## Steps

1. **Create `.claude/icm-archive/`** if it does not exist.

2. **Move everything Van Clief into `.claude/icm-archive/`**:
   - `_core/`
   - `workspaces/workspace-builder/`
   - `workspaces/cowork-station-builder/` (if present)
   - `workspaces/script-to-animation/` (if present)
   - `workspaces/voice-driven-animation/` (if present)
   - `workspaces/course-deck-production/` (if present)
   - `workspaces/` folder itself if now empty
   - `CLAUDE.md` (root ICM file)
   - `LICENSE`
   - `README.md`
   - `.gitignore`

3. **Leave untouched**:
   - The built workspace folder (produced in stage 03)
   - `.claude/` itself
   - Anything the user placed manually

4. **Confirm**:

   ```
   Done. ICM archived to .claude/icm-archive/.
   Your workspace is live. Run setup to begin.
   ```

## Root After Done

```
./
└── {{PROJECT_NAME}}/          (the built workspace -- setup runs here next)
    ├── CLAUDE.md
    ├── CONTEXT.md
    ├── setup/
    ├── _context/
    ├── shared/
    ├── skills/
    └── stages/
.claude/
└── icm-archive/               (everything Van Clief -- out of the way, still referenceable)
    ├── CLAUDE.md
    ├── _core/
    ├── LICENSE
    ├── README.md
    └── workspaces/
```

## Rules

- Do not run until all Stage 05 checks pass
- Archive is permanent -- ICM scaffolding has done its job
- The workspace's own setup takes over from here
