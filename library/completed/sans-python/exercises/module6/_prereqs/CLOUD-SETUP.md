# Module 6 — Cloud Setup & Dry-Run-First Prerequisites

Every Module 6 artifact runs **locally and offline by default.** You do not need a cloud account, a GPU, or any
paid API key to build, run, and test these artifacts — the smoke path uses deterministic mocks and the Python
standard library. Real platforms are **opt-in**, behind `.env`, when you want to see an artifact run against the
actual stack.

## The rule: local done-when first, cloud opt-in second
- **Build and pass the gate locally.** Each artifact has a `smoke.py` (`python smoke.py`) and tests
  (`python -m pytest tests/`, or the stdlib fallback noted in its README). Both must pass offline before you
  reach for a real service. That is the artifact's done-when.
- **Then, optionally, bind the real platform.** Copy `.env.example` → `.env`, fill in the keys, and the
  artifact swaps the mock for the real service at its portable seam. Nothing in the graded path depends on it.

## Per-artifact opt-in services (all optional)
| Artifact | Real stack (opt-in) | Local default (always works) | `.env` keys |
|---|---|---|---|
| 01 terminal-coding-agent | Anthropic Claude (Agent SDK) | deterministic mock LLM + subprocess sandbox | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` |
| 02 production-rag-chatbot | Azure AI Search + Azure OpenAI/Anthropic; Docling | pure-Python in-memory index + stdlib parser + mock LLM | `AZURE_SEARCH_*`, `ANTHROPIC_API_KEY` / `AZURE_OPENAI_*` |
| 03 realtime-voice-assistant | Pipecat / LiveKit + Deepgram (STT) + Cartesia (TTS) | mock pipeline stages with simulated latency | provider keys per README |
| 04 issue-to-pr-agent | GitHub + GitHub Actions (fork, fine-grained PAT) | local git repo + mock CI (runs tests locally) | `GITHUB_TOKEN` (fine-grained, single repo) |

## Cost & safety guardrails (when you do go live)
- **Budget caps are on by default** — each artifact ships a cost ceiling; keep it low when testing against a
  real API. A breach stops the run.
- **Scoped credentials only.** Artifact 04: use a **fine-grained** PAT limited to a throwaway **fork**, with
  Contents + Pull-requests scope — never a classic token, never your main repo. The agent **never auto-merges**.
- **Tear down.** Cloud resources (an Azure AI Search index, etc.) cost money idle — delete them when done.
- **No secrets in git.** `.env` is git-ignored; only `.env.example` (no real values) is committed.

If a key is missing or a service is down, the artifact falls back to its local mock — it never hard-fails on a
missing cloud dependency. That is the dry-run-first contract.
