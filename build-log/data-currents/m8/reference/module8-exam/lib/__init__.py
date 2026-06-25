"""Shared store for the Module 8 diagnostic exam.

The corpus pipeline under exam is a distilled version of the Data Currents M7 pipeline:
ingest -> freshness check -> lineage capture -> freshness gate, over SQLite. The exam
ships a broken_pipeline.py with three injected defects and asks you to diagnose and fix
them. This package holds the schema and the helpers both the broken and fixed pipelines
share, so the only differences between them are the defects themselves.
"""
