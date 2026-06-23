"""
choose_tier.py
Tier-selection logic for the M5 Warehouse and Lakehouse module.

Given a natural-language access pattern, returns "warehouse" or "lakehouse".
Raises ValueError on an unrecognised pattern.

The decision encodes the real tradeoff from the Microsoft Fabric decision guide:

  WAREHOUSE (choose "warehouse")
  --------------------------------
  - Full T-SQL / DML surface: UPDATE, DELETE, MERGE, stored procedures.
  - Multi-table ACID transactions across fact and dimension tables.
  - BI dashboard and reporting tools (Power BI DirectQuery, SSRS, Tableau).
  - Structured, schema-on-write data with tight governance requirements.
  - Finance, sales, compliance, and operational reporting workloads.

  LAKEHOUSE (choose "lakehouse")
  --------------------------------
  - Open Delta / Parquet format: any engine can read without a license.
  - ML and data-science workloads: feature extraction, model training.
  - RAG corpus management: embed chunks, update incrementally, zero-copy.
  - Spark / Python / R / DuckDB analytics without a managed SQL endpoint.
  - Schema-on-read flexibility for exploratory and semi-structured data.
  - Time-travel and lineage: Delta log preserves every snapshot.

Reference:
  Microsoft Fabric documentation — "Warehouse vs. Lakehouse"
  https://learn.microsoft.com/en-us/fabric/data-warehouse/
          data-warehousing#compare-the-warehouse-and-the-sql-analytics-endpoint-of-the-lakehouse

Supported pattern keys (case-insensitive substrings; first match wins):
  warehouse  -> "bi", "dashboard", "t-sql", "tsql", "structured-query",
                "sql-endpoint", "reporting", "olap", "finance", "compliance",
                "multi-table", "acid", "dml", "power-bi", "powerbi",
                "dimensional", "fact-table"
  lakehouse  -> "ml", "machine-learning", "rag", "embedding", "open-format",
                "delta", "parquet", "spark", "data-science", "feature-store",
                "zero-copy", "time-travel", "lineage", "exploratory",
                "corpus", "semi-structured", "streaming"
"""

from __future__ import annotations

_WAREHOUSE_KEYWORDS = frozenset([
    "bi",
    "dashboard",
    "t-sql",
    "tsql",
    "structured-query",
    "sql-endpoint",
    "reporting",
    "olap",
    "finance",
    "compliance",
    "multi-table",
    "acid",
    "dml",
    "power-bi",
    "powerbi",
    "dimensional",
    "fact-table",
])

_LAKEHOUSE_KEYWORDS = frozenset([
    "ml",
    "machine-learning",
    "rag",
    "embedding",
    "open-format",
    "delta",
    "parquet",
    "spark",
    "data-science",
    "feature-store",
    "zero-copy",
    "time-travel",
    "lineage",
    "exploratory",
    "corpus",
    "semi-structured",
    "streaming",
])


def choose_tier(access_pattern: str) -> str:
    """Return "warehouse" or "lakehouse" for the given access pattern.

    Parameters
    ----------
    access_pattern:
        A short description of how the data will be consumed.
        Examples:
          "bi dashboard for sales reporting"  -> "warehouse"
          "rag corpus update with embeddings" -> "lakehouse"

    Returns
    -------
    str
        "warehouse" or "lakehouse".

    Raises
    ------
    ValueError
        If no known keyword matches the pattern.
    """
    normalised = access_pattern.lower()

    # Check warehouse keywords first (structured/governed access)
    for kw in _WAREHOUSE_KEYWORDS:
        if kw in normalised:
            return "warehouse"

    # Check lakehouse keywords (open-format / ML / exploratory)
    for kw in _LAKEHOUSE_KEYWORDS:
        if kw in normalised:
            return "lakehouse"

    raise ValueError(
        f"Unknown access pattern: {access_pattern!r}. "
        "Provide a pattern containing a recognised keyword. "
        f"Warehouse keywords: {sorted(_WAREHOUSE_KEYWORDS)}. "
        f"Lakehouse keywords: {sorted(_LAKEHOUSE_KEYWORDS)}."
    )
