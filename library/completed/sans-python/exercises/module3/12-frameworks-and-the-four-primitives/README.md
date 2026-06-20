# Exercise 12 — Frameworks and the Four Primitives

**Goal** — Re-implement the M2/07 complexity-ladder task in LangGraph and measure what the framework buys versus the from-scratch loop.

**Why** — A framework is only worth adopting if it solves a real problem in your architecture; this exercise makes the cost and benefit concrete before you build anything larger.

**Steps**

1. Open `module3-agent/` — the from-scratch ReAct harness you built in lessons 01–03.
2. Create `module3-agent/frameworks/langgraph_agent.py`. In it, re-implement the same task from lesson 01 (the toy goal that used one stub tool) as a LangGraph `StateGraph`:
   - Define a `TypedDict` state with at least `messages: list` and `turn: int`.
   - Add a `reason` node (calls the model) and an `act` node (calls the tool).
   - Wire a conditional edge from `act`: if the model signals done, go to `END`; otherwise loop back to `reason`.
   - Enable `SqliteSaver` checkpointing with a `thread_id` so the run is resumable.
3. Run both the from-scratch loop and the LangGraph version against the same task and print:
   - Number of lines of agent control code (excluding boilerplate).
   - Whether checkpointing is present and what it would take to add it to the from-scratch version.
   - One failure mode the LangGraph version handles automatically that the from-scratch version does not.
4. Write a `COMPARISON.md` (3–5 sentences) in `module3-agent/frameworks/`: when does the LangGraph version win, and when is the from-scratch version the right choice?

**Done when**

- `module3-agent/frameworks/langgraph_agent.py` runs to completion on the same task as the from-scratch loop.
- A checkpoint file is written to disk and the run resumes correctly if interrupted mid-execution.
- `COMPARISON.md` names one concrete reason to use each version based on the measured results — not opinion.

**Stretch** — Add a conditional edge that routes to a `human_review` node when the model's confidence is low (stub the confidence signal as a keyword in the output). Wire the `human_review` node to accept a string input and inject it back into state as a correction.
