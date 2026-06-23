"""
corpus_seed.py
Synthetic gold corpus that stands in for the M2 dbt gold output.

In production, the M2 pipeline (bronze -> silver -> gold MERGE in DuckDB/SQLite)
produces two gold tables:
  - source_documents  (doc_id, version_id, last_modified_at, content_hash)
  - chunks            (chunk_id, source_doc_id, source_doc_version,
                       corpus_version, text)

Here we materialise a ~30-document pandas DataFrame that reproduces those
columns so the M5 lakehouse code remains self-contained.  The text content
and category labels come from the M2 seed corpus (seeds/corpus_raw.csv).

CATEGORY COUNTS (deterministic, used by smoke.py assertions):
  computer-vision      : 6
  data-engineering     : 6
  interpretability     : 8
  mlops                : 5
  nlp                  : 5
  reinforcement-learning: 4
  Total                : 34  (30-doc target, rounded to round category numbers)

NOTE: content_hash values are deterministic md5 digests of (doc_id + text),
so they never change between runs.
"""

import hashlib
from datetime import datetime, timezone

import pandas as pd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash(doc_id: str, text: str) -> str:
    return hashlib.md5(f"{doc_id}:{text}".encode()).hexdigest()


_TS_V0 = "2025-06-01 00:00:00"   # version 0 timestamp (initial load)
_TS_V1 = "2025-07-15 00:00:00"   # version 1 timestamp (after corpus update)


# ---------------------------------------------------------------------------
# Public: build the initial (v0) gold corpus
# ---------------------------------------------------------------------------

_ROWS_V0 = [
    # (doc_id, title, text, category)
    # computer-vision (6)
    ("doc_0001", "A deep dive into computer vision architectures",
     "computer vision systems require careful engineering to scale. distributed processing, "
     "feature stores, and model registries are central. observability is critical: log inputs, "
     "outputs, and latency. versioning models and datasets prevents silent regressions.",
     "computer-vision"),
    ("doc_0008", "Survey of computer vision techniques",
     "practitioners adopting computer vision should invest in reproducibility. use deterministic "
     "seeds, pin dependency versions, and store intermediate artifacts. a/b testing and shadow "
     "deployments reduce rollout risk. evaluation suites must cover edge cases.",
     "computer-vision"),
    ("doc_0015", "Scaling computer vision with distributed systems",
     "this document covers the fundamentals of computer vision with a focus on production "
     "readiness. we discuss data pipelines, model training, and deployment strategies. key "
     "metrics include latency, throughput, and accuracy. teams should monitor drift and retrain "
     "regularly.",
     "computer-vision"),
    ("doc_0021", "Evaluating computer vision models",
     "computer vision systems require careful engineering to scale. distributed processing, "
     "feature stores, and model registries are central. observability is critical: log inputs, "
     "outputs, and latency. versioning models and datasets prevents silent regressions.",
     "computer-vision"),
    ("doc_0061", "Building robust computer vision workflows",
     "the evolution of computer vision has accelerated with transformer architectures. "
     "pre-training on large corpora followed by task-specific fine-tuning dominates. prompt "
     "engineering and retrieval-augmented generation extend capability without full retraining.",
     "computer-vision"),
    ("doc_0066", "A deep dive into computer vision architectures",
     "cost management in computer vision projects demands token budgeting, caching, and batching "
     "strategies. profiling inference reveals bottlenecks. quantization and distillation reduce "
     "serving costs while maintaining acceptable quality thresholds.",
     "computer-vision"),
    # data-engineering (6)
    ("doc_0003", "Introduction to data engineering pipelines",
     "this document covers the fundamentals of data engineering with a focus on production "
     "readiness. we discuss data pipelines, model training, and deployment strategies. key "
     "metrics include latency, throughput, and accuracy. teams should monitor drift and retrain "
     "regularly.",
     "data-engineering"),
    ("doc_0007", "Fine-tuning data engineering for domain adaptation",
     "practitioners adopting data engineering should invest in reproducibility. use deterministic "
     "seeds, pin dependency versions, and store intermediate artifacts. a/b testing and shadow "
     "deployments reduce rollout risk. evaluation suites must cover edge cases.",
     "data-engineering"),
    ("doc_0013", "Scaling data engineering with distributed systems",
     "cost management in data engineering projects demands token budgeting, caching, and batching "
     "strategies. profiling inference reveals bottlenecks. quantization and distillation reduce "
     "serving costs while maintaining acceptable quality thresholds.",
     "data-engineering"),
    ("doc_0022", "Survey of data engineering techniques",
     "practitioners adopting data engineering should invest in reproducibility. use deterministic "
     "seeds, pin dependency versions, and store intermediate artifacts. a/b testing and shadow "
     "deployments reduce rollout risk. evaluation suites must cover edge cases.",
     "data-engineering"),
    ("doc_0028", "Best practices for data engineering in production",
     "practitioners adopting data engineering should invest in reproducibility. use deterministic "
     "seeds, pin dependency versions, and store intermediate artifacts. a/b testing and shadow "
     "deployments reduce rollout risk. evaluation suites must cover edge cases.",
     "data-engineering"),
    ("doc_0031", "Optimizing data engineering latency",
     "data engineering systems require careful engineering to scale. distributed processing, "
     "feature stores, and model registries are central. observability is critical: log inputs, "
     "outputs, and latency. versioning models and datasets prevents silent regressions.",
     "data-engineering"),
    # interpretability (8)
    ("doc_0000", "Scaling interpretability with distributed systems",
     "this document covers the fundamentals of interpretability with a focus on production "
     "readiness. we discuss data pipelines, model training, and deployment strategies. key "
     "metrics include latency, throughput, and accuracy. teams should monitor drift and retrain "
     "regularly.",
     "interpretability"),
    ("doc_0006", "Evaluating interpretability models",
     "the evolution of interpretability has accelerated with transformer architectures. "
     "pre-training on large corpora followed by task-specific fine-tuning dominates. prompt "
     "engineering and retrieval-augmented generation extend capability without full retraining.",
     "interpretability"),
    ("doc_0012", "Building robust interpretability workflows",
     "cost management in interpretability projects demands token budgeting, caching, and batching "
     "strategies. profiling inference reveals bottlenecks. quantization and distillation reduce "
     "serving costs while maintaining acceptable quality thresholds.",
     "interpretability"),
    ("doc_0014", "Fine-tuning interpretability for domain adaptation",
     "practitioners adopting interpretability should invest in reproducibility. use deterministic "
     "seeds, pin dependency versions, and store intermediate artifacts. a/b testing and shadow "
     "deployments reduce rollout risk. evaluation suites must cover edge cases.",
     "interpretability"),
    ("doc_0018", "Optimizing interpretability latency",
     "interpretability systems require careful engineering to scale. distributed processing, "
     "feature stores, and model registries are central. observability is critical: log inputs, "
     "outputs, and latency. versioning models and datasets prevents silent regressions.",
     "interpretability"),
    ("doc_0020", "Scaling interpretability with distributed systems",
     "cost management in interpretability projects demands token budgeting, caching, and batching "
     "strategies. profiling inference reveals bottlenecks. quantization and distillation reduce "
     "serving costs while maintaining acceptable quality thresholds.",
     "interpretability"),
    ("doc_0023", "Evaluating interpretability models",
     "interpretability systems require careful engineering to scale. distributed processing, "
     "feature stores, and model registries are central. observability is critical: log inputs, "
     "outputs, and latency. versioning models and datasets prevents silent regressions.",
     "interpretability"),
    ("doc_0075", "Evaluating interpretability models",
     "the evolution of interpretability has accelerated with transformer architectures. "
     "pre-training on large corpora followed by task-specific fine-tuning dominates. prompt "
     "engineering and retrieval-augmented generation extend capability without full retraining.",
     "interpretability"),
    # mlops (5)
    ("doc_0011", "Fine-tuning mlops for domain adaptation",
     "practitioners adopting mlops should invest in reproducibility. use deterministic seeds, "
     "pin dependency versions, and store intermediate artifacts. a/b testing and shadow "
     "deployments reduce rollout risk. evaluation suites must cover edge cases.",
     "mlops"),
    ("doc_0019", "A deep dive into mlops architectures",
     "practitioners adopting mlops should invest in reproducibility. use deterministic seeds, "
     "pin dependency versions, and store intermediate artifacts. a/b testing and shadow "
     "deployments reduce rollout risk. evaluation suites must cover edge cases.",
     "mlops"),
    ("doc_0024", "Introduction to mlops pipelines",
     "mlops systems require careful engineering to scale. distributed processing, feature stores, "
     "and model registries are central. observability is critical: log inputs, outputs, and "
     "latency. versioning models and datasets prevents silent regressions.",
     "mlops"),
    ("doc_0036", "Evaluating mlops models",
     "this document covers the fundamentals of mlops with a focus on production readiness. we "
     "discuss data pipelines, model training, and deployment strategies. key metrics include "
     "latency, throughput, and accuracy. teams should monitor drift and retrain regularly.",
     "mlops"),
    ("doc_0085", "Monitoring mlops at scale",
     "mlops systems require careful engineering to scale. distributed processing, feature stores, "
     "and model registries are central. observability is critical: log inputs, outputs, and "
     "latency. versioning models and datasets prevents silent regressions.",
     "mlops"),
    # nlp (5)
    ("doc_0005", "Evaluating nlp models",
     "nlp systems require careful engineering to scale. distributed processing, feature stores, "
     "and model registries are central. observability is critical: log inputs, outputs, and "
     "latency. versioning models and datasets prevents silent regressions.",
     "nlp"),
    ("doc_0010", "Survey of nlp techniques",
     "this document covers the fundamentals of nlp with a focus on production readiness. we "
     "discuss data pipelines, model training, and deployment strategies. key metrics include "
     "latency, throughput, and accuracy. teams should monitor drift and retrain regularly.",
     "nlp"),
    ("doc_0047", "Scaling nlp with distributed systems",
     "the evolution of nlp has accelerated with transformer architectures. pre-training on large "
     "corpora followed by task-specific fine-tuning dominates. prompt engineering and "
     "retrieval-augmented generation extend capability without full retraining.",
     "nlp"),
    ("doc_0057", "Introduction to nlp pipelines",
     "practitioners adopting nlp should invest in reproducibility. use deterministic seeds, pin "
     "dependency versions, and store intermediate artifacts. a/b testing and shadow deployments "
     "reduce rollout risk. evaluation suites must cover edge cases.",
     "nlp"),
    ("doc_0117", "A deep dive into nlp architectures",
     "the evolution of nlp has accelerated with transformer architectures. pre-training on large "
     "corpora followed by task-specific fine-tuning dominates. prompt engineering and "
     "retrieval-augmented generation extend capability without full retraining.",
     "nlp"),
    # reinforcement-learning (4)
    ("doc_0032", "Building robust reinforcement learning workflows",
     "this document covers the fundamentals of reinforcement learning with a focus on production "
     "readiness. we discuss data pipelines, model training, and deployment strategies. key "
     "metrics include latency, throughput, and accuracy. teams should monitor drift and retrain "
     "regularly.",
     "reinforcement-learning"),
    ("doc_0041", "Scaling reinforcement learning with distributed systems",
     "practitioners adopting reinforcement learning should invest in reproducibility. use "
     "deterministic seeds, pin dependency versions, and store intermediate artifacts. a/b testing "
     "and shadow deployments reduce rollout risk. evaluation suites must cover edge cases.",
     "reinforcement-learning"),
    ("doc_0042", "Fine-tuning reinforcement learning for domain adaptation",
     "reinforcement learning systems require careful engineering to scale. distributed processing, "
     "feature stores, and model registries are central. observability is critical: log inputs, "
     "outputs, and latency. versioning models and datasets prevents silent regressions.",
     "reinforcement-learning"),
    ("doc_0051", "A deep dive into reinforcement learning architectures",
     "practitioners adopting reinforcement learning should invest in reproducibility. use "
     "deterministic seeds, pin dependency versions, and store intermediate artifacts. a/b testing "
     "and shadow deployments reduce rollout risk. evaluation suites must cover edge cases.",
     "reinforcement-learning"),
]

# Expected category counts at v0 — exported so tests can import the oracle
EXPECTED_CATEGORY_COUNTS_V0: dict[str, int] = {
    "computer-vision":       6,
    "data-engineering":      6,
    "interpretability":      8,
    "mlops":                 5,
    "nlp":                   5,
    "reinforcement-learning": 4,
}


def build_gold_corpus_v0() -> pd.DataFrame:
    """Return the initial gold corpus DataFrame (version 0 of the Delta table).

    Schema mirrors M2 gold source_documents extended with title/text/category
    for warehouse query convenience:
      doc_id           : str   primary key
      title            : str
      text             : str   cleaned body (lowercase, whitespace-normalised)
      content_hash     : str   md5(doc_id:text)
      category         : str
      last_modified_at : str   ISO-8601 timestamp
    """
    records = []
    for doc_id, title, text, category in _ROWS_V0:
        records.append({
            "doc_id":           doc_id,
            "title":            title,
            "text":             text,
            "content_hash":     _hash(doc_id, text),
            "category":         category,
            "last_modified_at": _TS_V0,
        })
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# v1: a controlled update to demonstrate Delta versioning + time-travel
#
# We update doc_0000 to a new body (simulating a corpus refresh).
# The change bumps content_hash and last_modified_at for that document only.
# All other rows are identical to v0, so the DataFrame row counts are the same
# but ONE row differs — the smoke test asserts this difference.
# ---------------------------------------------------------------------------

_UPDATED_DOC_ID   = "doc_0000"
_UPDATED_TEXT_V1  = (
    "interpretability at scale demands mechanistic probes, saliency maps, and "
    "concept activation vectors. distributed tracing links each model decision "
    "back to its training data. safety teams use these tools to audit behaviour "
    "before production rollouts."
)


def build_gold_corpus_v1() -> pd.DataFrame:
    """Return the updated gold corpus DataFrame (version 1 of the Delta table).

    Only doc_0000 changes.  All other rows are byte-identical to v0.
    """
    df = build_gold_corpus_v0().copy()
    mask = df["doc_id"] == _UPDATED_DOC_ID
    df.loc[mask, "text"]             = _UPDATED_TEXT_V1
    df.loc[mask, "content_hash"]     = _hash(_UPDATED_DOC_ID, _UPDATED_TEXT_V1)
    df.loc[mask, "last_modified_at"] = _TS_V1
    return df


# Constants exported for smoke / test assertions
UPDATED_DOC_ID  = _UPDATED_DOC_ID
UPDATED_TEXT_V1 = _UPDATED_TEXT_V1
