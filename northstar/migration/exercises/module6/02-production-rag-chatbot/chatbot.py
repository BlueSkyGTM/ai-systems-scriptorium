"""chatbot.py -- retrieve, then answer with citations.

The answer is grounded: it is built from retrieved chunks and every answer carries
the citation of the chunk it drew from. A regulated assistant that asserts a
retention period with no source is a liability, so a citation is not decoration --
it is the artifact a compliance reviewer audits.

On the smoke path the generator is a deterministic mock LLM: it composes the answer
from the top chunk's text, so the output is reproducible and the citation is real.
A real model (Anthropic or Azure OpenAI) is an opt-in swap behind the same
`generate` signature; both are guarded imports and neither runs offline.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, List

from guardrail import Guardrail, refusal
from retriever import Retriever, Retrieved

# Generator signature: (question, retrieved chunks) -> answer text.
Generator = Callable[[str, List[Retrieved]], str]


@dataclass
class Answer:
    text: str
    citations: List[str] = field(default_factory=list)
    blocked: bool = False
    refused_no_context: bool = False

    def cites(self, doc_id: str) -> bool:
        return any(doc_id in c for c in self.citations)


def mock_llm(question: str, hits: List[Retrieved]) -> str:
    """Deterministic offline generator.

    Grounds the answer in the top chunk verbatim and appends an explicit citation.
    No network, no model. This is the same 'deterministic policy at the seam' move
    the harness lessons use: a real model plugs in here with no contract change.
    """
    if not hits:
        return ""
    top = hits[0]
    cite = top.citation
    return (
        f"Based on the policy: {top.chunk.text.strip()}\n\n"
        f"[source: {cite}]"
    )


def anthropic_llm(question: str, hits: List[Retrieved]) -> str:  # pragma: no cover - needs key
    """Opt-in real generator via the Anthropic SDK. Requires ANTHROPIC_API_KEY.

    [verify: anthropic Messages API + system prompt with cite-or-refuse instruction]
    """
    try:
        import anthropic  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Real LLM needs `pip install anthropic`") from exc

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    context = "\n\n".join(f"[{h.citation}]\n{h.chunk.text}" for h in hits)
    system = (
        "You are a compliance assistant. Answer ONLY from the provided context. "
        "Every claim must carry a [source: ...] citation taken from the context. "
        "If the context does not contain the answer, say you do not know."
    )
    # [verify: current model id via the claude-api skill -- set ANTHROPIC_MODEL in .env;
    # do not hardcode a model id from memory]
    msg = client.messages.create(
        model=os.environ["ANTHROPIC_MODEL"],
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"}],
    )
    return msg.content[0].text


class Chatbot:
    """The end-to-end answer path: guardrail -> retrieve -> generate -> guardrail."""

    def __init__(
        self,
        retriever: Retriever,
        guardrail: Guardrail | None = None,
        generator: Generator = mock_llm,
    ) -> None:
        self._retriever = retriever
        self._guardrail = guardrail or Guardrail()
        self._generate = generator

    def answer(self, question: str, k: int = 4) -> Answer:
        # Input rail (operator surface: guardrail gate).
        v_in = self._guardrail.screen_input(question)
        if v_in.blocked:
            return Answer(text=refusal(v_in), blocked=True)

        hits = self._retriever.retrieve(question, k=k)
        if not hits:
            # CRAG-style refusal: no relevant context, so do not fabricate.
            return Answer(
                text="I don't have a policy source for that. No answer generated.",
                refused_no_context=True,
            )

        text = self._generate(question, hits)

        # Output rail.
        v_out = self._guardrail.screen_output(text)
        if v_out.blocked:
            return Answer(text=refusal(v_out), blocked=True)

        citations = [h.citation for h in hits]
        return Answer(text=text, citations=citations)


if __name__ == "__main__":
    from index import default_index
    from ingest import ingest_corpus

    here = os.path.dirname(os.path.abspath(__file__))
    bot = Chatbot(Retriever(default_index(ingest_corpus(os.path.join(here, "corpus")))))
    a = bot.answer("How long must customer account records be retained?")
    print(a.text)
    print("citations:", a.citations)
