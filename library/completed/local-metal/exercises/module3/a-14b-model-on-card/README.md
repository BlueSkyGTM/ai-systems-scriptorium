# Exercise: A 14B Model on the Card

**Goal:** Start the module-3 throughline file `MODELS.md`. Record the serving layer and the
first model: `qwen2.5-coder:14b`, its quantization tag, and its VRAM footprint on your 16 GB
card.

**Why:** `HARDWARE.md` documented the metal. `SETUP.md` documented the runtime. `MODELS.md`
completes the stack by recording what you actually serve and proving the model fits on-card.
This file is a portfolio artifact: a hiring manager reading it can see the exact model,
the quantization you chose, and the VRAM number that confirms zero overflow. The next lesson,
"Record the Stack," adds a `## Sample Response` section and ships `check_models.py`, the
validator that enforces the fits-on-card invariant. This exercise creates the file that validator
will read.

---

## Files You Are Editing

The throughline file lives here and stays here:

```
exercises/module3/a-14b-model-on-card/MODELS.md
```

Do not move or rename this file. Later lessons read it from this exact path.

---

## Steps

### Step 1: Pull the Model and Confirm It Loaded

If you have not done so yet, pull the model and verify it is resident in VRAM:

```bash
ollama pull qwen2.5-coder:14b
ollama ps
```

Confirm `100% GPU` in the PROCESSOR column before recording VRAM numbers. If you see a CPU
fraction, the model has spilled; drop to a smaller tag.

Check VRAM usage while the model is loaded:

```bash
nvidia-smi
```

Note the Memory-Usage reading (on the reference build, roughly `11254MiB / 16380MiB`).

### Step 2: Create MODELS.md

Create the file at `exercises/module3/a-14b-model-on-card/MODELS.md` using exactly this
template. Fill in your real values where the reference values appear:

```markdown
# Model Stack

The serving layer and the models on the rig, with their VRAM footprint. Read by check_models.py.

## Serving Layer

Ollama version: 0.30.10
Docker version: 27.3.1
Endpoint: http://localhost:11434

## Models

| Model | Quantization | Size on Disk | VRAM Used | VRAM Total |
|-------|--------------|--------------|-----------|------------|
| qwen2.5-coder:14b | Q4_K_M | 9.0 GB | 11.0 GB | 16.0 GB |
```

Keep the column order exactly as shown: Model, Quantization, Size on Disk, VRAM Used,
VRAM Total. The `VRAM Used` value must be less than `VRAM Total`; that inequality is the
zero-overflow invariant `check_models.py` will enforce in the next lesson.

To find your Ollama version:

```bash
ollama --version
```

To find your Docker version (if Docker is installed):

```bash
docker --version
```

---

## Note for Readers Without Hardware Yet

If you do not have the rig yet, paste the reference values shown in the template above.
The validator that arrives in "Record the Stack" checks that the file is complete and that
`VRAM Used` is less than `VRAM Total`; it checks structure and the invariant, not live truth.
The reference build values satisfy both.

---

## Done When

The file `exercises/module3/a-14b-model-on-card/MODELS.md` exists and contains:

- A filled `## Serving Layer` section with Ollama version, Docker version, and the endpoint.
- A `## Models` table with at least one row: `qwen2.5-coder:14b`, its Q4_K_M quantization,
  disk size, VRAM used, and VRAM total.
- A `VRAM Used` value that is less than `VRAM Total` in every row.

Full validation arrives with `check_models.py` in the "Record the Stack" lesson. That lesson
also adds the `## Sample Response` section to this file and runs the validator end to end.

---

## Stretch

Add a second row to the `## Models` table for a swap-in model. `codellama:13b` (approximately
7.4 GB on disk) is a clean choice: pull it, confirm `100% GPU` via `ollama ps`, read the VRAM
figure from `nvidia-smi`, and record it. Both rows should satisfy the fits-on-card invariant.
The validator will check every row in the table, so a second entry gets checked automatically
when `check_models.py` ships next lesson.
