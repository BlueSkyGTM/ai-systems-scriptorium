# Module 4: Streaming and Change-Data-Capture

The nightly pipeline from Modules 2 and 3 is fine until a source cannot wait for the night. A
compliance edit lands at 9 a.m.; a price changes; a user updates a document the model is about to cite.
A batch that reloads at 2 a.m. serves the old answer for seventeen hours. This module builds the leg
that handles those sources: change-data-capture turning row-level changes into a stream, the Kafka
substrate that carries it, and a freshness monitor that measures lag in seconds instead of hours.

You do not stand up a Kafka cluster here. You learn the streaming model the way it actually works, and
you build a faithful in-process simulation of it so the whole pipeline runs offline and tested. The
vocabulary is real: topics, partitions, offsets, consumer groups, at-least-once delivery. The
correctness is real too: every streamed change applies through the same content-hash merge from Module
2, so a streamed update and a batch update land identically, only faster.

## What This Module Covers

**Streaming vs Batch** is the decision, and the freshness SLO is the decision variable. A source that
must be in the index in seconds streams; a source that can wait hours batches. You choose per source,
not per system, and you write the SLO down before you build anything.

**Change-Data-Capture** is the bridge from a database to a stream. CDC turns a table's inserts, updates,
and deletes into change events the consumer applies with the same merge as the batch load. The streamed
change is correct because it reuses the batch's correctness; it is just faster.

**Kafka: Topics and Consumer Groups** is the substrate that carries the events. A topic is a durable,
partitioned append log; an offset marks each record's position; a consumer group divides the partitions
so each is read by one consumer, and uncommitted offsets give at-least-once delivery, which is why
idempotency matters.

**The Streaming Freshness Monitor** closes the module. Streaming freshness is a continuous
event-to-applied lag measured per source, breaching at seconds scale. It is the same staleness question
Module 2 asked of the batch leg, measured three orders of magnitude tighter and all the time.

## Who This Is For

You finished Module 3: you have a batch pipeline that runs itself and alerts on breach. Now you add the
real-time leg for the sources that cannot wait. You model and consume the stream; you do not operate the
broker.

## The Artifact

You build `module4-streaming/`, an offline, standard-library simulation of a Kafka streaming pipeline: a
partitioned topic with offsets, a consumer group with at-least-once delivery, a CDC source emitting
change events, a consumer that applies each event through the Module 2 merge, and a lag monitor. It
extends the same corpus store, so a streamed change is just a faster path to the tables Module 1 queries.
Module 5 is where the batch and streaming legs land: the warehouse and the lakehouse.

## Prerequisites

- Modules 2 and 3 complete (the merge and the orchestrated pipeline)
- Python 3.11+; the streaming simulation is standard library only, fully offline
- Comfort with the Module 2 content-hash merge and the freshness SLO idea

## Time Estimate

Each lesson runs 70 to 100 minutes including its exercise. The Kafka simulation lesson is the densest;
the vocabulary rewards going slowly once.
