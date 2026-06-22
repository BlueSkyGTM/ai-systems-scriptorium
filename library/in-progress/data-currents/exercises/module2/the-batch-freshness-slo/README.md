# Exercise: The Batch Freshness SLO

**Goal**: Extend `module2-ingestion/` so that every ingest run writes an audit row, per-source SLO
targets define the freshness contract, and `freshness_check.py` exits non-zero the moment any source
goes stale.

**Why**: A gate that produces a reliable non-zero exit on staleness is the measurable equivalent of a
freshness promise; without it, you have a number on a wiki page, not an enforced contract.

---

## Steps

This exercise extends and closes `module2-ingestion/`. Find the directory, run the existing `smoke.py`
gate, and confirm it passes before adding anything. You are continuing a build, not starting one.

**1. Add the two new tables to `db/schema.sql`.**

```sql
CREATE TABLE corpus_loads (
    load_id       TEXT PRIMARY KEY,
    source_id     TEXT NOT NULL,
    status        TEXT NOT NULL,
    loaded_at     TEXT NOT NULL,
    rows_ingested INTEGER NOT NULL
);
CREATE TABLE freshness_slos (
    source_id     TEXT PRIMARY KEY,
    max_age_hours INTEGER NOT NULL
);
```

Apply the schema update without dropping existing tables (use `CREATE TABLE IF NOT EXISTS` or check
first). The `source_documents` and `chunks` tables from the merge lesson must remain intact.

**2. Seed `freshness_slos` in `db/seed_slos.py` (or inline in `smoke.py`).**

Insert two rows:

- `('corpus_raw', 25)`: the nightly batch source; stale after 25 hours.
- `('corpus_raw_realtime', 2)`: the near-real-time source; stale after 2 hours.

**3. Extend `ingest.py` to append a `corpus_loads` row on every run.**

After `merge_gold` completes, insert one row into `corpus_loads`:

- `load_id`: a UUID (use `uuid.uuid4()` from the standard library).
- `source_id`: the name of the source being loaded (e.g. `'corpus_raw'`).
- `status`: `'success'` when `merge_gold` returns without raising; `'failure'` if it raises.
- `loaded_at`: `datetime.utcnow().isoformat()`.
- `rows_ingested`: the count of rows processed (not just new versions; total rows passed to `merge_gold`).

Do not alter `merge_gold` itself; the audit write happens in the caller.

**4. Build `freshness_check.py`.**

Use exactly this query and branching logic (locked; do not alter):

```python
rows = conn.execute("""
    SELECT s.source_id, s.max_age_hours, MAX(cl.loaded_at) AS last_load_ts
    FROM freshness_slos s
    LEFT JOIN corpus_loads cl
        ON cl.source_id = s.source_id AND cl.status = 'success'
    GROUP BY s.source_id, s.max_age_hours
""").fetchall()

for row in rows:
    if row["last_load_ts"] is None:
        age_hours, is_stale = float("inf"), True       # never loaded -> stale
    else:
        last_load = datetime.fromisoformat(row["last_load_ts"])
        age_hours = (now - last_load).total_seconds() / 3600
        is_stale  = age_hours > row["max_age_hours"]
# exit non-zero if ANY source is stale -> the gate
```

`freshness_check.py` run directly should print a line per source (source_id, age in hours, stale
or fresh) and exit non-zero if any source is stale, zero if all are fresh.

**5. Finalize `smoke.py` with three new assertions.**

Add these checks at the end of the existing `smoke.py` gate:

- **Fresh assertion**: seed a `corpus_loads` row for `corpus_raw` with a `loaded_at` timestamp
  one hour ago (inside the 25-hour SLO). Run `freshness_check.py` (or call the check function
  directly). Assert exit code is 0.
- **Stale assertion**: seed a `corpus_loads` row for `corpus_raw` with a `loaded_at` timestamp
  30 hours ago (outside the 25-hour SLO). Run `freshness_check.py`. Assert exit code is non-zero.
- **M1 query agreement**: run M1's freshness-breach query (verbatim from the `ctes-and-the-diagnostic-chain`
  lesson) against the same `corpus_loads` and `freshness_slos` tables. Assert it returns exactly
  `corpus_raw` as the stale source.

The M1 freshness-breach query for reference:

```sql
WITH last_successful_load AS (
    SELECT source_id, MAX(loaded_at) AS last_load_ts
    FROM corpus_loads
    WHERE status = 'success'
    GROUP BY source_id
),
freshness_status AS (
    SELECT
        s.source_id, s.last_load_ts,
        f.max_age_hours,
        (
            (julianday('now') - julianday(s.last_load_ts)) * 24
        ) > f.max_age_hours AS is_stale
    FROM last_successful_load s
    JOIN freshness_slos f ON s.source_id = f.source_id
)
SELECT source_id, last_load_ts, max_age_hours, is_stale
FROM freshness_status
WHERE is_stale
ORDER BY last_load_ts ASC;
```

Note: the SQLite-compatible age computation uses `julianday` arithmetic rather than interval
syntax; the semantics are identical to M1's DuckDB form.

---

## Done When

- `python freshness_check.py` exits 0 when all sources are inside their SLO window; exits non-zero
  when any source exceeds its target.
- `python smoke.py` exits 0 and prints a pass summary covering all assertions: the fresh source
  passes the check, the stale source fails the check, and the M1 freshness-breach query returns
  exactly the stale source.
- All checks run offline: standard library only (`sqlite3`, `uuid`, `datetime`, `subprocess`).

---

## Stretch

Add the `corpus_raw_realtime` source to the smoke gate. Seed it with a `loaded_at` timestamp 3
hours ago (outside its 2-hour SLO). Assert that `freshness_check.py` returns non-zero and that
the M1 query surfaces both `corpus_raw_realtime` and (if still stale) `corpus_raw`. This shows
how the two SLO targets behave differently: a nightly source tolerates a 25-hour window; the
near-real-time source goes stale three times faster.
