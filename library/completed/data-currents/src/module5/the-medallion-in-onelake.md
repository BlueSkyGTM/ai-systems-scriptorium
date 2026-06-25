# The Medallion in OneLake

Every team copies the corpus into its own store, and within a year the data platform is a dozen
stale duplicates with no clear source of truth. OneLake and shortcuts are the answer: one logical
lake for the whole tenant, one copy of the data, zero sprawl.

## What OneLake Actually Is

OneLake is Microsoft Fabric's single, unified, logical data lake for an entire tenant. Every
workspace in the tenant shares it; there are no per-team buckets to provision and no separate
storage accounts to wire together. Data lands once, in open Delta format, and every consumer in
the tenant reads the same copy. [MS-Learn OneLake overview:
https://learn.microsoft.com/fabric/onelake/onelake-overview]

The word "logical" matters. OneLake looks like a file system, but the namespace spans lakehouses,
warehouses, and workspaces without physical duplication. The AI team, the analytics team, and the
ML team all see the same paths; they are not copying files between buckets to share data.

## The Medallion as Storage Organization

The medallion you built in Module 2 was a transform pattern: bronze holds raw ingestion, silver
cleans it, gold shapes it for serving. In OneLake, that same bronze/silver/gold split becomes the
recommended way to organize a lakehouse's storage. Each layer maps to a folder; the gold folder is
what downstream consumers read. [MS-Learn medallion architecture:
https://learn.microsoft.com/fabric/onelake/onelake-medallion-lakehouse-architecture]

The organizational choice matters at scale. When you have one OneLake and one medallion structure,
a consumer looking for the curated corpus has one obvious place to look: the gold layer of the
lakehouse the data team owns. There is no question of which team's copy is fresher, because there
is only one copy.

## Shortcuts: Zero-Copy References

The mechanism that prevents duplication across workspaces is the shortcut. A OneLake shortcut is
a reference, not a copy: it points to data in another lakehouse, ADLS, or S3 and makes it appear
in your workspace's namespace without moving or duplicating the underlying bytes. The data stays at
the source; reads go through the OneLake namespace. [MS-Learn shortcuts:
https://learn.microsoft.com/fabric/onelake/onelake-shortcuts]

This is the production answer to the "every team copies the corpus" failure mode. The ML team
creates a shortcut in their workspace that targets the gold layer the data team owns. They read
the same Delta table, the same version, with no ETL, no sync job, and no risk of drift. When the
data team updates gold, the ML team's shortcut reflects it immediately.

## The Gold Corpus as the Gold Layer

The Delta corpus table you wrote in the lesson-2 artifact is a gold-layer table by the OneLake
definition: it holds cleaned, curated, retrieval-ready documents, and it is the layer consumers
query.

```python
# The gold corpus Delta table (from lesson 2) is the "gold layer" in OneLake terms:
write_deltalake(gold_path, gold_df, mode="overwrite")   # gold layer, open Delta format
# A OneLake SHORTCUT would point another workspace at gold_path with zero copy.
```

In a production Fabric deployment, `gold_path` is a folder inside the data team's lakehouse gold
layer. Another team creates a shortcut to that path, and their queries hit the same Delta table
with no copy and no pipeline to maintain.

## Core Concepts

- OneLake is one logical data lake per Fabric tenant: data lands once in open Delta format, and
  every workspace in the tenant reads the same copy with no per-team buckets.
- The medallion (bronze/silver/gold) is the recommended way to organize a OneLake lakehouse; the
  gold layer is the single folder downstream consumers read.
- A shortcut references data in another lakehouse, ADLS, or S3 without copying it; reads go
  through the OneLake namespace while the bytes stay at the source.
- The gold corpus Delta table from lesson 2 is exactly a gold-layer Delta table; a shortcut
  replaces the copy that would otherwise propagate stale data to every downstream team.

The cost of duplicate data is not storage; it is the moment an incident fires and no one can say
which copy was the one the model was actually reading.

<div class="claude-handoff" data-exercise="exercises/module5/the-medallion-in-onelake/">

**Build It in Claude Code**: Organize the corpus store as a single lake directory with bronze, silver, and gold subpaths; write the gold corpus as the gold-layer Delta table consumers read; then write a short `LAKE_LAYOUT.md` (or docstring) that names each layer's role and identifies one concrete location where a OneLake shortcut would replace a copy.

</div>
