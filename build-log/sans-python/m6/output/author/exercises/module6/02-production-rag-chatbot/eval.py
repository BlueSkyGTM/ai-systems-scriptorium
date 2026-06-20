"""eval.py -- the operator's acceptance gate.

Two metrics from the RAG triad (M2 evaluation), scored offline against the labeled
evalset:

  - retrieval precision: of the question's retrieved chunks, did the top result come
    from the document the label says holds the answer? (context relevance)
  - answer faithfulness: does the generated answer actually contain the facts the
    label expects, drawn from the cited source? (groundedness)

Both use deterministic checks here -- no LLM judge needed on the smoke path -- so the
gate is reproducible and runs in CI. The acceptance gate is a threshold on each
metric: below it, the build does not ship. That is the operator's go/no-go surface.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Callable, List

from chatbot import Answer, Chatbot
from retriever import Retriever


@dataclass
class EvalReport:
    n: int
    retrieval_precision: float
    answer_faithfulness: float
    per_item: List[dict]

    def passes(self, *, min_precision: float, min_faithfulness: float) -> bool:
        """The acceptance gate."""
        return (
            self.retrieval_precision >= min_precision
            and self.answer_faithfulness >= min_faithfulness
        )


def load_evalset(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)["items"]


def _faithful(answer: Answer, keywords: List[str]) -> bool:
    """Faithful == the answer text contains all expected facts (case-insensitive)."""
    text = answer.text.lower()
    return all(kw.lower() in text for kw in keywords)


def evaluate(
    chatbot: Chatbot,
    evalset: List[dict],
    *,
    k: int = 4,
    answer_fn: Callable[[Chatbot, str, int], Answer] | None = None,
) -> EvalReport:
    """Run the chatbot over the labeled set and score precision + faithfulness.

    `answer_fn` lets a test inject a degraded answerer (to prove a low-faithfulness
    build fails the gate) without touching the corpus.
    """
    if answer_fn is None:
        answer_fn = lambda bot, q, kk: bot.answer(q, k=kk)  # noqa: E731

    hits_correct = 0
    faithful_correct = 0
    per_item: List[dict] = []

    for item in evalset:
        q = item["question"]
        ans = answer_fn(chatbot, q, k)
        retrieved = chatbot._retriever.retrieve(q, k=k)
        top_doc = retrieved[0].chunk.doc_id if retrieved else ""
        precision_hit = top_doc == item["relevant_doc"]
        faithful_hit = _faithful(ans, item["answer_keywords"]) and ans.cites(
            item["relevant_doc"]
        )
        hits_correct += int(precision_hit)
        faithful_correct += int(faithful_hit)
        per_item.append(
            {
                "id": item["id"],
                "top_doc": top_doc,
                "expected_doc": item["relevant_doc"],
                "precision_hit": precision_hit,
                "faithful_hit": faithful_hit,
            }
        )

    n = len(evalset)
    return EvalReport(
        n=n,
        retrieval_precision=hits_correct / n if n else 0.0,
        answer_faithfulness=faithful_correct / n if n else 0.0,
        per_item=per_item,
    )


def build_default_chatbot() -> Chatbot:
    from index import default_index
    from ingest import ingest_corpus

    here = os.path.dirname(os.path.abspath(__file__))
    corpus = ingest_corpus(os.path.join(here, "corpus"))
    return Chatbot(Retriever(default_index(corpus)))


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    es = load_evalset(os.path.join(here, "corpus", "evalset.json"))
    report = evaluate(build_default_chatbot(), es)
    print(f"retrieval_precision = {report.retrieval_precision:.2f}")
    print(f"answer_faithfulness = {report.answer_faithfulness:.2f}")
    ok = report.passes(min_precision=0.8, min_faithfulness=0.8)
    print(f"acceptance gate (>=0.80 / >=0.80): {'PASS' if ok else 'FAIL'}")
