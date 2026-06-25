"""
lakehouse.py
Open-table-format (Delta Lake) layer for the M5 Warehouse and Lakehouse module.

This module writes the M2 gold corpus into a Delta table stored on the local
filesystem, exposing:
  - write_corpus_v0  : initial load -> Delta version 0
  - write_corpus_v1  : corpus update -> Delta version 1
  - read_latest      : latest snapshot (pandas DataFrame)
  - read_version     : time-travel read at an explicit version number
  - get_history      : list of version metadata dicts
  - get_version_num  : current (latest) version number
  - get_schema       : Delta schema object

The Delta table lives at <delta_path>/corpus_delta/ by default.
It is the open-format complement to the warehouse.py DuckDB query surface:
  - Lakehouse side: Delta format, readable by Spark/pandas/DuckDB zero-copy,
    ideal for ML feature extraction and RAG corpus updates.
  - Warehouse side: structured SQL endpoint (DuckDB), ideal for BI dashboards
    and T-SQL aggregations.

Engine: deltalake 1.6.0, pandas 3.x, pyarrow 24.x — fully offline.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from deltalake import DeltaTable, write_deltalake

# ---------------------------------------------------------------------------
# Default path — callers may override with delta_path parameter
# ---------------------------------------------------------------------------

HERE = Path(__file__).parent
DEFAULT_DELTA_PATH = str(HERE / "corpus_delta")


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def write_corpus_v0(df: pd.DataFrame, delta_path: str = DEFAULT_DELTA_PATH) -> int:
    """Write the initial gold corpus as Delta version 0 (overwrite / create).

    Parameters
    ----------
    df:
        The M2 gold corpus DataFrame.  Schema expected:
        doc_id, title, text, content_hash, category, last_modified_at.
    delta_path:
        Directory where the Delta table is created.

    Returns
    -------
    int
        The Delta version number after the write (always 0 on a fresh table).
    """
    write_deltalake(delta_path, df, mode="overwrite")
    return DeltaTable(delta_path).version()


def write_corpus_v1(df: pd.DataFrame, delta_path: str = DEFAULT_DELTA_PATH) -> int:
    """Write an updated gold corpus, creating Delta version 1.

    Uses mode="overwrite" so the full snapshot is replaced.  The previous
    snapshot is preserved in the Delta log and remains accessible via
    time-travel (read_version(path, 0)).

    Returns
    -------
    int
        The Delta version number after the write (1 on the second write).
    """
    write_deltalake(delta_path, df, mode="overwrite")
    return DeltaTable(delta_path).version()


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------

def read_latest(delta_path: str = DEFAULT_DELTA_PATH) -> pd.DataFrame:
    """Return the latest snapshot of the Delta table as a pandas DataFrame."""
    return DeltaTable(delta_path).to_pandas()


def read_version(version: int, delta_path: str = DEFAULT_DELTA_PATH) -> pd.DataFrame:
    """Time-travel read: return the Delta snapshot at *version*.

    Parameters
    ----------
    version:
        Integer Delta version (0 = initial write, 1 = first update, …).
    delta_path:
        Path to the Delta table directory.

    Returns
    -------
    pd.DataFrame
        The corpus as it existed at the requested version.

    Raises
    ------
    Exception
        If the version does not exist in the Delta log.
    """
    return DeltaTable(delta_path, version=version).to_pandas()


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def get_history(delta_path: str = DEFAULT_DELTA_PATH) -> list[dict]:
    """Return the version history of the Delta table.

    Each entry is a dict with at minimum:
      version, timestamp, operation, operationParameters.
    """
    return DeltaTable(delta_path).history()


def get_version_num(delta_path: str = DEFAULT_DELTA_PATH) -> int:
    """Return the current (latest) version number of the Delta table."""
    return DeltaTable(delta_path).version()


def get_schema(delta_path: str = DEFAULT_DELTA_PATH):
    """Return the Delta schema object for the corpus table."""
    return DeltaTable(delta_path).schema()


# ---------------------------------------------------------------------------
# Time-travel content_hash lookup (M6 lineage preview)
# ---------------------------------------------------------------------------

def get_content_hash_at_version(
    doc_id: str,
    version: int,
    delta_path: str = DEFAULT_DELTA_PATH,
) -> str | None:
    """Return the content_hash of *doc_id* as it existed at *version*.

    This is the building block for the M6 lineage store question:
    "What did this answer cite last week?"  The Delta transaction log
    preserves every snapshot, so we can answer that question exactly —
    no separate audit table needed.

    Returns None if doc_id is not present in that version's snapshot.
    """
    df = read_version(version, delta_path)
    row = df[df["doc_id"] == doc_id]
    if row.empty:
        return None
    return row.iloc[0]["content_hash"]
