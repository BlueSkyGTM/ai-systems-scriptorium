# Exercise 11 — Memory That Improves

## Goal

Extend `module3-agent/` with typed memory blocks, a skill library with register/search/call, a sleep-time consolidation stub, and a checkpoint/resume hook in the agent loop.

## Why

Memory that only stores and retrieves is a filing cabinet. Memory that consolidates, learns from execution, and survives failures is an asset — the difference between an agent that degrades over long runs and one that gets better.

## Steps

1. **Create `module3-agent/memory/blocks.py`.**
   - Implement a `BlockManager` class holding a dict of typed blocks: `human` (facts about the user), `persona` (agent role and tone), and any custom blocks you define.
   - Each block has a `content: str`, `capacity: int` (character limit), and `schema: dict` (allowed fields).
   - Implement `block_append(label, content)`: appends content; raises `BlockOverflowError` when capacity is exceeded.
   - Implement `block_replace(label, field, value)`: replaces a named field within a block's content (simple string substitution is fine for the stub).
   - Implement `block_summarize(label)`: calls `claude-haiku-4-5` with a summarization prompt and replaces the block content with the summary, freeing capacity.

2. **Create `module3-agent/memory/skills.py`.**
   - Implement a `SkillLibrary` class with:
     - `register(name, description, fn)`: stores the callable under `name` with its description.
     - `search(query, top_k=3) -> list[str]`: returns skill names whose descriptions best match the query (keyword overlap or embedding — your choice).
     - `call(name, **kwargs)`: looks up and calls the registered function; logs call + result to the episodic store from exercise 10.
   - Register at least two stub skills: `read_file(path)` and `write_file(path, content)`.

3. **Create `module3-agent/memory/sleep_agent.py`.**
   - Implement `consolidate(recall_store, block_manager, model="claude-haiku-4-5")`.
   - Read the 50 most recent entries from the episodic store (exercise 10's `EpisodicMemory.recent(50)`).
   - Build a summarization prompt and call the model. Write the summary into `block_manager.block_replace("human", "summary", summary)`.
   - Prune episodic entries older than a configurable `retention_hours` threshold.
   - This function runs outside the agent loop (simulated "sleep-time") — call it from a standalone script or test, not from inside a turn.

4. **Add checkpoint/resume to the agent loop.**
   - Define an `AgentCheckpoint` dataclass: `run_id`, `turn`, `messages`, `tool_results`, `memory_snapshot`, `timestamp`.
   - After each successful turn, serialize to `checkpoints/<run_id>/<turn>.json`.
   - Add a `--resume <run_id>` CLI flag. When passed, load the latest checkpoint for `run_id` and continue from `turn + 1`.
   - Verify that `messages` and `tool_results` from the checkpoint are correctly restored into the loop.

5. **Write tests.**
   - `test_blocks.py`: overflow triggers `BlockOverflowError`; `block_summarize` reduces content length.
   - `test_skills.py`: `register` + `search` returns the correct skill; `call` logs to episodic.
   - `test_checkpoint.py`: run 3 turns, interrupt after turn 2 (raise an exception), resume with `--resume`, assert turn 3 runs and `messages` contains all prior turns.

## Done when

- `python -m pytest module3-agent/tests/test_blocks.py module3-agent/tests/test_skills.py module3-agent/tests/test_checkpoint.py` passes with no errors.
- Running `python -m module3_agent.sleep_agent` on a store with at least 5 episodic entries writes a non-empty summary to the `human` block and prints the pruned count.
- Running the loop with `--resume <run_id>` starts from the correct turn and prints `[Resumed from checkpoint turn N]`.

## Stretch

Add a skill confidence score: track success/failure counts per skill call (via the episodic log). After 5 calls, promote skills with >80% success rate to `high_confidence=True`. In `search`, sort high-confidence skills above others when their descriptions match equally well.
