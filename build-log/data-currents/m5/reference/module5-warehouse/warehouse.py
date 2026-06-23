"""
warehouse.py
Structured warehouse-query surface for the M5 Warehouse and Lakehouse module.

DuckDB acts as the offline stand-in for Snowflake / BigQuery / Microsoft Fabric
Warehouse.  It reads the gold corpus from a pandas DataFrame (or from the Delta
parquet files directly) and runs aggregate SQL over it.

Design note — warehouse vs. lakehouse:
  - Warehouse (this file): structured SQL endpoint with full T-SQL-style DML,
    multi-table joins, and BI dashboard patterns.  Data is materialised into
    DuckDB.  Access pattern: "how many documents per category this quarter?"
  - Lakehouse (lakehouse.py): open Delta format, zero-copy readable by
    Spark, pandas, or DuckDB.  Access pattern: "give me the embedding-ready
    chunks for the RAG pipeline" or "what did doc_0000 look like last week?"

The warehouse is READ-ONLY in this module; writes go through the Delta table.

Engine: duckdb 1.5.x — in-memory, no external server.
"""

from __future__ import annotations

import duckdb
import pandas as pd


# ---------------------------------------------------------------------------
# Core query: document counts per category
# ---------------------------------------------------------------------------

def doc_count_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Return document counts grouped by category, sorted descending.

    Parameters
    ----------
    df:
        The gold corpus DataFrame.  Must contain a 'category' column.

    Returns
    -------
    pd.DataFrame
        Columns: category (str), doc_count (int64).
        Rows: one per distinct category, ordered by doc_count DESC.
    """
    result = duckdb.query(
        """
        SELECT
            category,
            COUNT(*) AS doc_count
        FROM df
        GROUP BY category
        ORDER BY doc_count DESC, category ASC
        """
    ).df()
    return result


# ---------------------------------------------------------------------------
# Secondary query: unique content_hash count per category
# ---------------------------------------------------------------------------

def unique_hash_count_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Return distinct content_hash counts per category.

    Useful for detecting near-duplicate documents within a category
    (a common data-quality check in a warehouse).

    Returns
    -------
    pd.DataFrame
        Columns: category (str), unique_hashes (int64).
        Ordered by category ASC.
    """
    result = duckdb.query(
        """
        SELECT
            category,
            COUNT(DISTINCT content_hash) AS unique_hashes
        FROM df
        GROUP BY category
        ORDER BY category ASC
        """
    ).df()
    return result


# ---------------------------------------------------------------------------
# Convenience: run arbitrary SQL against the corpus frame
# ---------------------------------------------------------------------------

def query(sql: str, df: pd.DataFrame) -> pd.DataFrame:
    """Execute *sql* against the corpus DataFrame bound as the table 'df'.

    The SQL must reference the DataFrame as 'df'.  Example:
        query("SELECT doc_id FROM df WHERE category = 'mlops'", corpus_df)

    Returns
    -------
    pd.DataFrame
        Query result.
    """
    return duckdb.query(sql).df()
