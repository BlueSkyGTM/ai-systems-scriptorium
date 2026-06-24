The user wants me to generate the `broken_pipeline.py` file for Module 8 of "Data Currents". This is a deliberately corrupted version of M7's `pipeline_flow.py` with 3 specific defects:

1. **Defect 1**: `batch_now_ts` hardcoded to `"2099-01-01"` → batch freshness breach always fires
2. **Defect 2**: `capture_lineage` skips `record_verdict` → lineage chain is incomplete
3. **Defect 3**: `freshness_gate` has `retries=2` (should be 0) → gate doesn't fail loud

I need to create a believable, well-structured pipeline that:
- Uses vendored lib from M7 reference (same path pattern)
- Has all the expected components: `batch_now_ts`, `capture_lineage`, `freshness_gate`
- Contains the 3 defects injected subtly but detectably
- Is syntactically correct Python 3.11+
- Has the M7 pipeline structure (multi-source corpus ingestion)
- Can be diagnosed with SQL queries on sqlite3 DBs (corpus + lineage)

Let me design this as a multi-source corpus pipeline. The key components:

1. **Source ingestion** — multiple source documents (API, batch, file) with timestamps
2. **Batch processing** — `batch_now_ts` is used as the reference "now" for freshness checks
3. **Lineage tracking** — `capture_lineage` records source_document → derived_document edges, including verdict edges
4. **Freshness gate** — checks SLA with retries config
5. **Storage** — writes to sqlite DBs (corpus_store.db, lineage.db)

Let me think about the M7 reference structure. M7 is "multi-source corpus pipeline". It has:
- `corpus_store` — stores document versions
- `lineage` — stores source→derived relationships
- `pipeline_flow` — orchestrates ingestion with freshness checks

The file should look like a coherent pipeline someone wrote, with the defects hidden in plain sight. The defects should be:
- A hard-coded date somewhere in batch_now_ts (perhaps a "TODO: make this dynamic" comment or a recent edit)
- capture_lineage missing the record_verdict call (perhaps only capturing source→doc but not doc→verdict)
- freshness_gate defaulting to retries=2

Let me write a complete, realistic pipeline. It needs to:
- Be runnable (will be run by smoke.py)
- Write to sqlite3 databases that diagnose.py can query
- Have functions like `freshness_gate`, `capture_lineage`, `run_pipeline`
- Have the 3 defects

I'll use a vendored lib pattern. The pipeline produces:
- `outputs/corpus.db` — document store with source_document_versions, batches tables
- `outputs/lineage.db` — lineage_edges table
- `outputs/verdicts.db` — record_verdict outputs

Let me write this carefully. I'll make the pipeline:

1. Ingest 3 sources (api_poller, batch_loader, file_watcher)
2. Build source_document versions per source
3. Run a freshness check
4. Process into derived corpus documents
5. Capture lineage edges
6. Run verdicts
7. Write everything to sqlite

Here's the structure:

```python
"""
broken_pipeline.py
Module 8 — The Diagnostic Exam
Multi-source corpus pipeline with THREE injected defects.

Find them with diagnose.py, then fix in fix.py.
"""
import os, sqlite3, time, uuid, hashlib, json, random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Vendored lib from M7 reference
from lib.corpus_store import CorpusStore
from lib.lineage import LineageGraph
from lib.freshness import FreshnessGate, SLABreach
from lib.sources import api_source, batch_source, file_source
from lib.verdicts import record_verdict

random.seed(42)

OUTPUT_DIR = Path("outputs")
CORPUS_DB = OUTPUT_DIR / "corpus.db"
LINEAGE_DB = OUTPUT_DIR / "lineage.db"

# ============================================================
# Defect 1 (HIDDEN): batch_now_ts hardcoded to 2099-01-01
# This makes the batch-freshness breach ALWAYS fire because
# every source document will appear to be stale relative to
# a "now" 75 years in the future.
# ============================================================
BATCH_NOW_TS = "2099-01-01T00:00:00+00:00"  # TODO: dynamic per-batch
```

Actually, let me think more carefully. The defect should be subtle — it should be such that the pipeline still RUNS but produces a degraded/corrupted state. The freshness breach fires but doesn't stop the pipeline (because of Defect 3: retries=2 swallows it).

Let me also think about what diagnose.py would query:
- Query 1: Find the freshness breach (look for SLA breach records vs batch_now_ts)
- Query 2: Find the hardcoded 2099 date
- Query 3: Find the missing record_verdict lineage edge
- Query 4: Find the gate retries=2 setting
- Query 5: ...
- Query 6: ...

Let me write a self-contained pipeline. I'll make lib imports optional/graceful, or better yet, make this fully self-contained so it doesn't depend on lib (since lib is from M7 reference and the student might not have it). Actually the spec says "Imports vendored lib/ from M7 reference (same path pattern)" — so lib is expected to exist.

But for robustness, I'll write it so it falls back to inline implementations if lib isn't available. Actually no — let me just write it assuming lib exists, since that's the M7 reference contract.

Wait, but I need this to be RUNNABLE for smoke.py. If lib doesn't exist, it will fail to import. The spec says the constraint is "Imports vendored lib/ from M7 reference (same path pattern)" — so we assume it's there.

Hmm, but actually, for the smoke test to be self-contained, maybe I should make the pipeline self-contained. Let me re-read the spec.

"Imports vendored lib/ from M7 reference (same path pattern)" — this is a constraint on the MODULE, meaning M7's lib is available.

OK so the pipeline imports from lib. Let me write it that way but make the imports resilient.

Actually, to make this maximally useful as a reference artifact, I'll write a self-contained pipeline that defines everything inline (so it can run standalone), but uses `lib.*` patterns where they'd naturally appear in M7. Let me use a try/except import pattern so it works both ways.

Actually no — for the purpose of this artifact, the cleanest approach is to write a pipeline that:
1. Defines its core data structures and functions inline (self-contained)
2. Uses sqlite3 directly (as the spec allows for diagnose.py)
3. Has the three defects clearly present

This makes the file runnable for smoke.py and gradable. Let me design this.

Pipeline architecture:
- `Source` — represents a data source with name, freshness_sla_minutes, last_event_ts
- `SourceDocument` — a version of data from a source, with content_hash
- `Batch` — a collection of source_documents processed together with batch_now_ts
- `LineageEdge` — source_document → derived_document or derived_document → verdict
- `Verdict` — the answer derived from the corpus

Storage:
- `corpus.db`:
  - `source_documents(id, source, content_hash, event_ts, batch_id, created_at)`
  - `batches(id, now_ts, created_at)`
  - `derived_documents(id, batch_id, content_hash, created_at)`
  - `verdicts(id, derived_doc_id, verdict, created_at)`
  - `sla_breaches(id, source, event_ts, batch_now_ts, sla_minutes, created_at)`
- `lineage.db`:
  - `lineage_edges(id, src_type, src_id, dst_type, dst_id, batch_id, created_at)`

Pipeline flow:
1. `create_batch()` — creates a batch with batch_now_ts (DEFECT 1)
2. `ingest_sources()` — pulls from sources, creates source_documents, checks freshness
3. `freshness_gate()` — checks SLA breaches (DEFECT 3: retries=2)
4. `build_derived_docs()` — combines source documents
5. `capture_lineage()` — records edges (DEFECT 2: skips record_verdict)
6. `record_verdict()` — derives the answer
7. `commit()` — writes all to sqlite

Let me write this out.

```python
"""
broken_pipeline.py
====================
Module 8: The Diagnostic Exam — BROKEN multi-source corpus pipeline.

This file is the corrupted variant of M7's pipeline_flow.py.
Three defects have been injected. Run it, then use diagnose.py to
locate them with SQL, then produce fix.py with the corrections.

Defects (DO NOT READ IF YOU WANT TO SOLVE THE EXAM):
  1. batch_now_ts is hardcoded to the far future → freshness breach always fires
  2. capture_lineage skips the record_verdict edge → lineage chain incomplete
  3. freshness_gate retries=2 → gate does not fail loud

This file is intentionally runnable; it writes the corpus and lineage
databases that diagnose.py inspects.
"""
from __future__ import annotations
import hashlib
import json
import os
import random
import sqlite3
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

random.seed(42)

# Vendored M7 reference lib (graceful if absent — falls back to inline impls).
try:
    from lib.sources import poll_sources  # type: ignore
    _HAVE_LIB = True
except Exception:
    _HAVE_LIB = False

OUTPUT_DIR = Path(os.environ.get("M8_OUTPUT_DIR", "outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CORPUS_DB = OUTPUT_DIR / "corpus.db"
LINEAGE_DB = OUTPUT_DIR / "lineage.db"

ISO_FMT = "%Y-%m-%dT%H:%M:%S%z"

# ----------------------------------------------------------------------
# Defect 1 lives here: BATCH_NOW_TS is frozen to 2099-01-01, which means
# every source document will appear stale relative to the batch clock.
# In the original M7 pipeline this value was computed as datetime.now(timezone.utc).
# ----------------------------------------------------------------------
BATCH_NOW_TS = "2099-01-01T00:00:00+00:00"

PIPELINE_VERSION = "8.0.0-broken"

# ----------------------------------------------------------------------
# Source catalog — each source has an SLA expressed in minutes.
# ----------------------------------------------------------------------
SOURCE_CATALOG = [
    {"name": "api_poller",   "sla_minutes": 60},
    {"name": "batch_loader", "sla_minutes": 1440},
    {"name": "file_watcher", "sla_minutes": 360},
]
```

Now the data classes and functions. Let me make this complete.

I'll write a complete, runnable, well-structured pipeline. Let me make it production-quality-looking (because students are debugging it) but with the 3 subtle defects.

Let me think about what the gate does with retries=2. In a "fail loud" gate with retries=0, the first breach raises immediately. With retries=2, the gate retries 2 times then... maybe just logs and continues? That's the defect — it should fail loud (raise) but instead swallows the breach.

Let me design `freshness_gate`:

```python
def freshness_gate(breaches, retries=2):
    """
    Fail loud if any SLA breach is recorded.
    
    M7 spec: retries=0 — first breach aborts the batch.
    """
    if not breaches:
        return True
    for attempt in range(retries + 1):
        if attempt == retries:
            # final attempt — should raise but currently just logs
            print(f"[freshness_gate] WARN: {len(breaches)} breach(es) on attempt {attempt+1}/{retries+1}")
            return False  # defect: returns instead of raising
    return True
```

Hmm, let me make it clearer. With retries=0:
- attempt 0 == retries(0) → final attempt → should RAISE

With retries=2:
- attempt 0, 1, 2 — never reaches the "raise" branch because... hmm, with retries=2, attempt 2 == retries(2), so it WOULD reach the final branch.

Let me redesign. The defect is that retries=2 means the gate swallows breaches during retries 0 and 1, then on retry 2 it should fail loud but instead returns False (continues).

Actually a cleaner design: the gate tries `retries + 1` times. On each attempt it checks breaches. If breaches exist, it waits and retries until retries exhausted. With retries=0, the FIRST breach immediately raises. With retries=2, the gate retries twice (logging each time) and then... should also raise on the final attempt. But the defect could be: the final-attempt raise is missing or commented out, OR the retries=2 means the gate effectively tolerates the breach (returns False = "degraded but continue" instead of raising).

Let me make it: the gate raises SLABreach only if `retries == 0`. If retries > 0, it logs and continues in degraded mode. This makes the defect: with retries=2, the breach is logged but pipeline continues, whereas it should fail loud.

Actually that's overcomplicated. Let me simplify:

```python
class SLABreach(Exception):
    pass

def freshness_gate(breaches, retries=2):
    """
    Enforce freshness SLA. With retries=0 (M7 default), any breach raises.
    With retries>0, the gate tolerates breaches (DEGRADED MODE).
    """
    for attempt in range(retries):
        if breaches:
            time.sleep(0.01)  # would normally re-check
            continue
        return True
    if breaches:
        if retries == 0:
            raise SLABreach(f"{len(breaches)} breach(es)")
        # retries > 0: log and continue (THIS IS THE DEFECT)
        print(f"[freshness_gate] DEGRADED: {len(breaches)} breach(es) tolerated with retries={retries}")
        return False
    return True
```

Hmm, this is getting complex. Let me just make the defect clear: with retries=2, the gate never raises. The fix is to set retries=0.

Actually, I think the cleanest design is:

```python
def freshness_gate(breaches, *, retries=2):
    """
    Fail-loud freshness gate.
    
    Contract (M7 spec):
      retries == 0  →  first breach aborts the batch (raises SLABreach)
      retries  > 0  →  re-check N times, abort on final if still breached
    
    BUG: retries default is 2, not 0. This means the pipeline runs in
    degraded mode rather than aborting — exactly the silent-failure mode
    the SLA was supposed to prevent.
    """
    if not breaches:
        return True
    
    for attempt in range(1, retries + 1):
        # In a real system we'd re-poll sources here.
        if not breaches:
            return True
    
    # Final attempt.
    if retries == 0:
        raise SLABreach(f"freshness breach: {len(breaches)} source(s) stale")
    
    # BUG PATH: retries > 0 means we get here and... just return False.
    # Should be: raise SLABreach(...)
    return False
```

This is cleaner. The defect is: when retries > 0 (and it's 2 by default), the final-attempt branch returns False instead of raising. The fix: set retries=0 so the `retries == 0` branch fires and raises.

Wait, that's a bit weird because the fix should be "retries=0" but the code also has a second bug (the return False should be a raise). Let me re-read the spec.

"Defect 3: freshness_gate has retries=2 (should be 0) → gate doesn't fail loud"

So the ONLY defect is retries=2. The fix is simply retries=0. So the code should be:

```python
def freshness_gate(breaches, *, retries=2):
    """Fail-loud freshness gate. retries=0 means first breach aborts."""
    if not breaches:
        return True
    for attempt in range(retries):
        # would re-poll; in this simulation breaches don't clear
        pass
    raise SLABreach(f"freshness breach after {retries} retries: {len(breaches)} source(s) stale")
```

Wait, with retries=0, `range(0)` is empty, so it goes straight to raise. With retries=2, it loops twice (doing nothing useful) then raises. In both cases it raises. That doesn't show the defect.

Hmm. Let me think differently. The defect should be such that with retries=2 the gate does NOT fail loud, but with retries=0 it does.

```python
def freshness_gate(breaches, *, retries=2):
    """
    Fail-loud freshness gate.
    
    With retries=0: raise SLABreach on first breach (fail loud).
    With retries>0: log and continue in degraded mode (tolerant).
    """
    if not breaches:
        return True
    
    if retries == 0:
        raise SLABreach(f"freshness breach: {len(breaches)} source(s) stale")
    
    # retries > 0: degrade silently
    for attempt in range(retries):
        print(f"[freshness_gate] retry {attempt+1}/{retries}: {len(breaches)} breach(es)")
    print(f"[freshness_gate] DEGRADED MODE: continuing with {len(breaches)} stale source(s)")
    return False
```

This is clean. The defect is clear: `retries=2` (default) causes degraded mode instead of fail-loud. Fix: `retries=0`.

OK now Defect 2: capture_lineage skips record_verdict.

```python
def capture_lineage(graph, batch_id, source_docs, derived_docs, verdicts):
    """
    Record lineage edges: source_doc → derived_doc, derived_doc → verdict.
    """
    # Source → derived edges
    for sd in source_docs:
        for dd in derived_docs:
            if dd.source_refs and sd.id in dd.source_refs:
                graph.add_edge("source_document", sd.id, "derived_document", dd.id, batch_id)
    
    # BUG (Defect 2): the verdict edge is missing.
    # Should be:
    #   for v in verdicts:
    #       graph.add_edge("derived_document", v.derived_doc_id, "verdict", v.id, batch_id)
    # but this block