# The DAG: Tasks and Dependencies

A pipeline you run by hand is not a system; it is a checklist you hope no one skips. You `python extract.py`, then `python ingest.py`, then `python transform.py`, in that order, because you know the order. The scheduler does not know the order unless you tell it, and you tell it with a graph.

That graph is the DAG: a directed acyclic graph of tasks, where an arrow from A to B means "B cannot start until A finishes." The scheduler reads the graph, not the calendar. It runs each task the moment its upstream completes, in parallel where possible, and refuses to start a task whose dependency failed.

## What Makes a Graph a DAG

Three properties, all load-bearing. Directed: every dependency has a direction; extract feeds ingest, not the other way around. Acyclic: no cycle exists, so the scheduler can always find a task with no unsatisfied upstream, start there, and work forward. A cycle means no such starting point exists, and the pipeline deadlocks before it runs. Graph: multiple tasks, multiple edges, a topology the scheduler can traverse.

The "acyclic" constraint is the one engineers violate. A retry loop that re-enqueues a task, a feed-forward that depends on a task downstream of it: both introduce cycles the scheduler will catch at validation time, not at midnight when you expect the load to be done.

## A Task Is a Unit of Work

In Prefect, you mark a function as a task with `@task`. The decorator tells the runtime to treat the call as a node in the graph, track its state, and make its return value available to downstream tasks.

```python
from prefect import flow, task, get_run_logger

@task(name="ingest")
def ingest(csv_path: str, db_path: str) -> dict:
    """Run the M2 idempotent MERGE (bronze -> silver -> gold). Returns the load summary."""
    summary = run_ingest(csv_path=csv_path, db_path=db_path)
    return summary
```

The return value is the contract. The task does one thing and returns evidence it did it: a path, a summary dict, a status flag. The next task receives that evidence as its input; that handoff is the dependency edge.

## The Flow Wires Tasks into a DAG

A flow is the graph container. When you call one task and pass its return into another, you declare an edge. Prefect sees that `ingest` receives `csv_path` from `extract`, so `ingest` depends on `extract`. No separate dependency declaration: the data flow is the graph.

```python
@flow(name="corpus-pipeline")
def pipeline_flow(run_date, corpus_csv, db_path):
    csv_path         = extract(run_date=run_date, corpus_csv=corpus_csv)
    ingest_summary   = ingest(csv_path=csv_path, db_path=db_path)        # depends on extract
    transform_status = transform(ingest_summary=ingest_summary, db_path=db_path)  # depends on ingest
    freshness_results = freshness_gate(db_path=db_path)                  # depends on transform
    return {"ingest_summary": ingest_summary, "freshness_results": freshness_results}
```

Read it as a graph: `extract -> ingest -> transform -> freshness_gate`. Each arrow is a result passed as an argument. If `ingest` raises, Prefect marks it failed, skips `transform` and `freshness_gate`, and surfaces the failure at the flow level. Nothing downstream runs on a broken upstream.

## The Airflow Vocabulary (and Why It Matches)

Airflow is the industry-standard orchestrator. Azure Data Factory offers managed Apache Airflow jobs in Microsoft Fabric. [MS-Learn Apache Airflow jobs in Fabric: https://learn.microsoft.com/fabric/data-factory/apache-airflow-jobs-concepts] In Airflow, you declare tasks as operators and set dependencies explicitly with `>>`:

```python
extract_task >> ingest_task >> transform_task >> freshness_task
```

Prefect expresses the same edge by passing one task's return into the next call. The graph is identical; the syntax differs. If you move this pipeline from an offline Prefect runner to a Fabric Airflow cluster, the four tasks stay the same and the dependency topology stays the same. What changes is the declaration style, not the contract. [DAG concept: https://learn.microsoft.com/azure/aks/airflow-overview]

The important fact: the scheduler does not care how you declared the edge. It cares that the edge exists and is acyclic. Once it reads the graph, it runs tasks in topological order: no task starts before its upstream reports success.

## Core Concepts

- A DAG encodes a pipeline as tasks with typed dependencies; the scheduler runs tasks in topological order, and nothing starts until its upstream succeeds.
- A task's return value is the dependency edge: passing it into the next task call is how you declare that the second task depends on the first.
- "Acyclic" is the enforced constraint: any cycle means no topological order exists, and the scheduler rejects the graph before the first run.
- Airflow's `task_a >> task_b` and Prefect's result-passing express the same edge; the graph topology and the scheduler contract are identical.

<div class="claude-handoff" data-exercise="exercises/module3/the-dag-tasks-and-dependencies/">

**Build It in Claude Code**: Seed `module3-orchestration/` and write `pipeline_flow.py`, a Prefect flow that declares four `@task` functions (extract, ingest, transform, freshness_gate) and wires them into a `@flow` by passing each task's return value as the next task's input argument; the ingest task calls the M2 `run_ingest` loader from `module2-ingestion/ingest.py`. Run the flow offline with `python pipeline_flow.py` and prove the tasks execute in topological order (extract before ingest, ingest before transform, transform before freshness_gate) by asserting against the returned ingest summary.

</div>
