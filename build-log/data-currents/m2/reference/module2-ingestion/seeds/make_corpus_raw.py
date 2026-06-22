"""
seeds/make_corpus_raw.py
Generate seeds/corpus_raw.csv — a synthetic corpus of 120 documents.

Columns mirror the made-with-ml labeling schema:
  doc_id, created_on, title, body, category

Fixed seed = 42 for full determinism.
Run:  python seeds/make_corpus_raw.py
"""

import csv
import os
import random
from datetime import datetime, timedelta

SEED = 42
N_DOCS = 120
OUT_PATH = os.path.join(os.path.dirname(__file__), "corpus_raw.csv")

CATEGORIES = [
    "nlp", "computer-vision", "mlops", "data-engineering",
    "reinforcement-learning", "interpretability",
]

TITLE_TEMPLATES = [
    "Introduction to {topic} pipelines",
    "Scaling {topic} with distributed systems",
    "Best practices for {topic} in production",
    "A deep dive into {topic} architectures",
    "Monitoring {topic} at scale",
    "Optimizing {topic} latency",
    "Survey of {topic} techniques",
    "Building robust {topic} workflows",
    "Evaluating {topic} models",
    "Fine-tuning {topic} for domain adaptation",
]

BODY_TEMPLATES = [
    (
        "This document covers the fundamentals of {topic} with a focus on "
        "production readiness. We discuss data pipelines, model training, "
        "and deployment strategies. Key metrics include latency, throughput, "
        "and accuracy. Teams should monitor drift and retrain regularly."
    ),
    (
        "{topic} systems require careful engineering to scale. Distributed "
        "processing, feature stores, and model registries are central. "
        "Observability is critical: log inputs, outputs, and latency. "
        "Versioning models and datasets prevents silent regressions."
    ),
    (
        "Practitioners adopting {topic} should invest in reproducibility. "
        "Use deterministic seeds, pin dependency versions, and store "
        "intermediate artifacts. A/B testing and shadow deployments reduce "
        "rollout risk. Evaluation suites must cover edge cases."
    ),
    (
        "The evolution of {topic} has accelerated with transformer architectures. "
        "Pre-training on large corpora followed by task-specific fine-tuning "
        "dominates. Prompt engineering and retrieval-augmented generation extend "
        "capability without full retraining."
    ),
    (
        "Cost management in {topic} projects demands token budgeting, "
        "caching, and batching strategies. Profiling inference reveals "
        "bottlenecks. Quantization and distillation reduce serving costs "
        "while maintaining acceptable quality thresholds."
    ),
]

BASE_DATE = datetime(2025, 1, 1)


def make_csv():
    rng = random.Random(SEED)
    rows = []
    for i in range(N_DOCS):
        doc_id = f"doc_{i:04d}"
        category = rng.choice(CATEGORIES)
        topic = category.replace("-", " ")
        title_tmpl = rng.choice(TITLE_TEMPLATES)
        body_tmpl = rng.choice(BODY_TEMPLATES)
        title = title_tmpl.format(topic=topic)
        body = body_tmpl.format(topic=topic)
        days_offset = rng.randint(0, 365)
        created_on = (BASE_DATE + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        rows.append({
            "doc_id": doc_id,
            "created_on": created_on,
            "title": title,
            "body": body,
            "category": category,
        })
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["doc_id", "created_on", "title", "body", "category"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT_PATH}")


if __name__ == "__main__":
    make_csv()
