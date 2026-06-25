# Open Table Formats: Delta and Iceberg

A plain folder of Parquet files cannot tell you what it looked like yesterday, and two writers
arriving at the same second can corrupt it. An open table format fixes both problems by placing a
transaction log in front of the files: every write is a log entry, every read consults the log, and
every earlier snapshot is still there.

That last property is the one that matters for a RAG corpus. It is called time-travel, and it is
what makes M6's lineage store possible.

## The Transaction Log

Delta Lake stores each write as a JSON commit entry inside `_delta_log/`. Iceberg does the same
with its own manifest tree. The Parquet data files on disk are immutable; the log decides which
files are "current." When you overwrite a table, the old data files stay on disk and the log gains
a new entry pointing at the replacement files.

Writing two corpus versions is two log entries:

```python
from deltalake import DeltaTable, write_deltalake

def write_corpus_v0(df, delta_path):
    write_deltalake(delta_path, df, mode="overwrite")   # creates Delta version 0
    return DeltaTable(delta_path).version()

def write_corpus_v1(df, delta_path):
    write_deltalake(delta_path, df, mode="overwrite")   # version 1; v0 still in the log
    return DeltaTable(delta_path).version()
```

`version()` returns `0` after the first write and `1` after the second. The log already holds both.

## Reading Any Version

Because the log is append-only, you can reconstruct the table at any prior commit by replaying only
the entries up to that point. The `DeltaTable` constructor accepts a `version` argument:

```python
def read_version(version, delta_path):
    """Return the Delta snapshot at *version* (0 = initial, 1 = first update, ...)."""
    return DeltaTable(delta_path, version=version).to_pandas()

def get_history(delta_path):
    return DeltaTable(delta_path).history()   # list of version metadata
```

Call `read_version(0, path)` after two writes and you get the original corpus, not the current one.
Call `read_version(1, path)` and you get the update. The underlying Parquet files for both still
exist on disk; the log is the map.

The equivalent in SQL is `VERSION AS OF 0` or `TIMESTAMP AS OF '2024-01-01'`. The semantics are
identical: the log reconstructs the requested snapshot without touching the live table.

## What ACID Buys You

Without the transaction log, two concurrent writers on a Parquet folder will corrupt each other's
metadata. Delta's log commits are atomic: a write either lands as a complete entry or it does not.
Schema changes are validated against the existing metadata before the commit is accepted, so a write
that would break readers is rejected at the log level, not discovered by the next query.

Iceberg offers the same guarantees with a different log structure. In Microsoft Fabric, Delta and
Iceberg tables in OneLake interoperate through metadata virtualization: a Delta table is readable as
an Iceberg table and vice versa, without copying data.
[OneLake Iceberg: https://learn.microsoft.com/fabric/onelake/onelake-iceberg-tables]

## The Caveat: Retention Is Bounded

Time-travel is not infinite. Delta's `VACUUM` command removes data files older than a configurable
retention threshold (default: seven days). Once the files are vacuumed, the log entries that
reference them remain, but the data behind those entries is gone. Time-travel to a version whose
files have been vacuumed raises an error. Plan your retention window against the lineage window your
pipeline needs.
[MS-Learn Delta time travel: https://learn.microsoft.com/fabric/data-engineering/delta-lake-time-travel]

## Time-Travel as the Lineage Primitive

The content-hash MERGE from M2 records what a document looked like when it changed. The Delta log
records what the whole table looked like at every write. Together they answer a lineage question that
neither can answer alone: "What did this specific document's content look like at version N?"

```python
def get_content_hash_at_version(doc_id, version, delta_path):
    """What did this document's content look like at an earlier version?
       The Delta log preserves every snapshot, so we answer exactly."""
    df = read_version(version, delta_path)
    row = df[df["doc_id"] == doc_id]
    return None if row.empty else row.iloc[0]["content_hash"]
```

M6 calls this function. The warehouse you are building now is the store it reads.

## Core Concepts

- An open table format (Delta, Iceberg) adds a transaction log in front of immutable Parquet files;
  every write is a log entry, not a file overwrite.
- Time-travel reads the table as it existed at any prior version by replaying log entries up to that
  point; `DeltaTable(path, version=n)` is the offline equivalent of `VERSION AS OF n`.
- ACID guarantees come from the log: a write is atomic, schema changes are validated before commit,
  and two concurrent writers cannot silently corrupt the table.
- Delta time-travel is bounded by `VACUUM` retention; once old data files are removed, those log
  entries become unreadable, so lineage windows must fit inside the retention window.

<div class="claude-handoff" data-exercise="exercises/module5/open-table-formats-delta-and-iceberg/">

**Build It in Claude Code**: Write the gold corpus DataFrame to a Delta table using `write_corpus_v0` (version 0), change one document's text and write again using `write_corpus_v1` (version 1), then call `read_version(0, path)` to confirm it returns the original content while `read_version(1, path)` returns the updated content; assert that the changed document's `content_hash` differs between the two snapshots using `get_content_hash_at_version`; and print the full version history with `get_history`.

</div>
