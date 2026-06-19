# Module 3 · Agent Engineering — Phases 14–16 Extract

> Source: `phases/14-agent-engineering/` (42 lessons), `phases/15-autonomous-systems/` (22 lessons), `phases/16-multi-agent-and-swarms/` (25 lessons) — 89 lessons total. Each phase `README.md` is a stub; all content lives in per-lesson `docs/en.md`.
> These three phases form **Module 3's agent track**: the single-agent loop (Phase 14) → long-horizon autonomous + safety systems (Phase 15) → multi-agent coordination and swarms (Phase 16). The arc moves from "one agent that works" to "one agent that runs for hours safely" to "many agents that coordinate."
> Lesson type markers: **Build** = hands-on code; **Learn** = concept/survey; **Learn + Build** = concept with implementation; **Learn (capstone)** = end-of-module synthesis.
> `[GAP 2: complexity ladder]` tags any lesson whose genuine topic is the should-you-build-an-agent / single-vs-multi / workflow-vs-agent decision (per CONTEXT.md Target 7).

## Phase 14 — Agent Engineering

1. ### 01 · The Agent Loop: Observe, Think, Act — **Build** · Python · ~60min
   Builds the canonical ReAct loop (Thought/Action/Observation) from stdlib in under 200 lines — a message buffer, tool registry, stop condition, turn budget, and observation formatter — the five ingredients that separate an agent from a chatbot. Frames the 2026 shift from prompt-based `Thought:` tokens to native model reasoning (Responses API, encrypted reasoning passthrough) and notes every modern harness (Claude Agent SDK, OpenAI Agents SDK, LangGraph, AutoGen v0.4) still runs this loop under the hood.
   **Tools/Frameworks:** Python stdlib, ReAct (Yao 2023), toy LLM, tool registry.

2. ### 02 · ReWOO and Plan-and-Execute: Decoupled Planning — **Build** · Python · ~60min
   ReWOO's Planner/Worker/Solver split decouples planning from execution: one plan DAG up front, parallel evidence fetches, one solver call — ~5× fewer tokens and +4% accuracy on HotpotQA versus interleaved ReAct, with per-node failure localization and a distillable 7B planner. Generalizes into LangChain's Plan-and-Execute (with a replanner) and Plan-and-Act (synthetic plan data for 30–50 step web/mobile agents).
   **Tools/Frameworks:** Python stdlib, ReWOO (Xu 2023), Plan-and-Execute (LangChain), Plan-and-Act.

3. ### 03 · Reflexion: Verbal Reinforcement Learning — **Build** · Python · ~60min
   Reflexion (Actor/Evaluator/Self-Reflector + episodic memory) fixes failures in natural language instead of gradients: after a failed trial the agent writes a reflection, stores it, and conditions the next trial on it — beating ReAct on ALFWorld/HotpotQA and setting then-SOTA on HumanEval without a single weight update. Three evaluator types (scalar, heuristic, self-evaluated); names the production descendants (Letta sleep-time compute, Claude Code `CLAUDE.md` learnings, `/learn-rule`).
   **Tools/Frameworks:** Python stdlib, Reflexion (Shinn 2023), episodic memory buffer.

4. ### 04 · Tree of Thoughts and LATS: Deliberate Search — **Build** · Python · ~75min
   Turns reasoning into search: ToT grows a tree of "thoughts" with LLM self-evaluation per node (Game of 24: 4% → 74% with GPT-4), and LATS unifies ToT + ReAct + Reflexion under MCTS (HumanEval pass@1 92.7%). Builds a stdlib BFS ToT and a toy LATS select/expand/simulate/backprop loop, with the cost-reality test for when search's token multiplier is worth it.
   **Tools/Frameworks:** Python stdlib, Tree of Thoughts (Yao 2023), LATS (Zhou 2024), MCTS/UCT.

5. ### 05 · Self-Refine and CRITIC: Iterative Output Improvement — **Build** · Python · ~60min
   Self-Refine runs one LLM in three roles (generate/feedback/refine) for +20 absolute across 7 tasks; CRITIC hardens the feedback step by routing verification through external tools (search, code interpreter, calculator, test runner) because LLMs are unreliable at self-verification on hard facts. Maps directly to Anthropic's "evaluator-optimizer" workflow and the OpenAI Agents SDK output-guardrail loop, with the generate-verify-external-refine-stop cycle as the 2026 default.
   **Tools/Frameworks:** Python stdlib, Self-Refine (Madaan 2023), CRITIC (Gou 2023), external verifiers.

6. ### 06 · Tool Use and Function Calling — **Build** · Python · ~60min
   Toolformer's self-supervised "keep annotation only if execution reduces next-token loss" through BFCL V4's 2026 evaluation composition (40% agentic, 30% multi-turn, 10% live, 10% hallucination), with the finding that single-turn calling is near-solved and failures concentrate in memory, dynamic decision-making, long-horizon chains, and hallucination detection. Builds a stdlib tool registry with schema validation, argument coercion, and execution sandboxing.
   **Tools/Frameworks:** Python stdlib, Toolformer, BFCL V4, JSON Schema tool definitions, Anthropic `input_schema` / OpenAI `function.parameters`.

7. ### 07 · Memory: Virtual Context and MemGPT — **Build** · Python · ~75min
   MemGPT maps context management to OS virtual memory — main context = RAM, external store = disk, memory tools = page in/out — solving overflow, dilution, and persistence that bigger windows don't fix (a 4k-window agent with external memory catches long-horizon facts a 128k baseline misses). Builds the two-tier pattern (main + searchable external) with the `core_memory_*` / `archival_memory_*` interrupt-style tool surface that Letta and Mem0 inherit.
   **Tools/Frameworks:** Python stdlib, MemGPT (Packer 2023), vector/KV/graph external store, memory-as-interrupt.

8. ### 08 · Memory Blocks and Sleep-Time Compute (Letta) — **Build** · Python · ~75min
   Letta's 2026 rewrite of MemGPT adds typed, editable memory blocks (Human/Persona/user-defined) across three tiers (core/recall/archival) and a sleep-time agent that consolidates memory asynchronously off the critical path — fixing latency, memory rot, and structure loss. Builds a scripted two-agent loop where a primary serves responses and a background sleep-time agent consolidates blocks between turns (the pattern behind Claude Code learnings and pro-workflow `/learn`).
   **Tools/Frameworks:** Python stdlib, Letta, memory blocks (`block_append`/`replace`/`summarize`), sleep-time compute.

9. ### 09 · Hybrid Memory: Vector + Graph + KV (Mem0) — **Build** · Python · ~75min
   Mem0 wires three parallel stores behind one `add`/`search` surface — vector for semantic similarity, KV for O(1) fact lookup, graph (Mem0g) for relationship reasoning — with a weighted-sum fusion score over relevance, importance, and recency. The argument: a single store is always wrong for two of the three query classes every production agent issues in one session; this is the 2026 production standard for external memory.
   **Tools/Frameworks:** Python stdlib, Mem0 (Chhikara 2025), vector store, KV store, graph store (Mem0g), fusion scoring.

10. ### 10 · Skill Libraries and Lifelong Learning (Voyager) — **Build** · Python · ~75min
    Voyager treats executable code as a skill — named, retrievable by description similarity, composable, and refined by execution feedback — via an automatic curriculum, a skill library, and an iterative prompting mechanism (Minecraft: 3.3× more unique items, 8.5× faster stone tools). This is the reference architecture for the 2026 Claude Agent SDK skills / skillkit pattern, where capabilities are programs loaded on demand rather than re-derived each session.
    **Tools/Frameworks:** Python stdlib, Voyager (Wang 2024), skill library, Claude Agent SDK skills, skillkit.

11. ### 11 · Planning with HTN and Evolutionary Search — **Build** · Python · ~75min
    Covers the two planning cases LLM planners miss: provably-correct plans (Hierarchical Task Networks, where ChatHTN interleaves symbolic decomposition with LLM fallback so every plan is sound by construction) and machine-checkable optimization (AlphaEvolve's evolutionary code search, which only works where a fast deterministic evaluator exists). Builds a toy HTN planner and a toy evolutionary search in stdlib; both use the LLM as amplifier, not replacement.
    **Tools/Frameworks:** Python stdlib, HTN, ChatHTN (2025), AlphaEvolve (DeepMind 2025), MAP-elites.

12. ### 12 · Anthropic's Workflow Patterns: Simple Over Complex — **Learn + Build** · Python · ~60min `[GAP 2: complexity ladder]`
    Schluntz & Zhang's Dec 2024 distinction between workflows (predefined code paths, engineers own the graph) and agents (dynamic tool-use, model owns the graph), with five workflow patterns — prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer — that cover most production cases. The core complexity-ladder argument: start with direct API calls, add a workflow when steps are predictable, reach for an agent only when the next step genuinely depends on the prior result; frameworks add layers that obscure prompts and invite premature complexity.
    **Tools/Frameworks:** Python stdlib, Anthropic five workflow patterns, augmented-LLM (search/tools/memory), context-engineering framing.

13. ### 13 · LangGraph: Stateful Graphs and Durable Execution — **Learn + Build** · Python · ~75min
    LangGraph models an agent as a state machine: typed immutable state, pure-function nodes, conditional edges, and a checkpoint written after every step so a failed 40-step run resumes from step 38, not zero. Four capabilities (durable execution, streaming, human-in-the-loop, comprehensive memory) across three topologies (supervisor, peer-to-peer swarm, hierarchical nested subgraphs); builds a stdlib state graph with a checkpoint/resume cycle.
    **Tools/Frameworks:** LangGraph, `StateGraph`, checkpointers (SQLite/Postgres/Redis), supervisor/swarm/hierarchical topologies.

14. ### 14 · AutoGen v0.4: Actor Model and Agent Framework — **Learn + Build** · Python · ~75min
    AutoGen v0.4's Jan 2025 redesign around the actor model — private state + inbox + handler, messages as the only IPC — delivering fault isolation per actor, natural concurrency, and distribution as just different transport. Three API layers (Core/AgentChat/Extensions), RoundRobin and Selector group chats, the Magentic-One reference team; now in maintenance mode as Microsoft Agent Framework (Oct 2025) becomes the successor. Builds a stdlib actor runtime and ports a two-agent code-review flow onto it.
    **Tools/Frameworks:** AutoGen v0.4, actor model, Microsoft Agent Framework, `AssistantAgent`/`UserProxyAgent`/GroupChat.

15. ### 15 · CrewAI: Role-Based Crews and Flows — **Learn + Build** · Python · ~75min
    CrewAI's four primitives (Agent/Task/Crew/Process) split into two shapes: Crews (autonomous, role-based, exploratory) and Flows (event-driven, deterministic, auditable), with the blunt production recommendation to "start with a Flow." Covers Sequential vs Hierarchical vs planned-Consensus processes, the `@tool`/`BaseTool` wiring, four memory types, and the three failure modes (prompt-bloat, manager-LLM tax, brittle handoffs). Builds a stdlib three-agent researcher/writer/editor crew.
    **Tools/Frameworks:** CrewAI 0.86, Agent/Task/Crew/Process, `@tool` decorator, `output_pydantic`, Flows.

16. ### 16 · OpenAI Agents SDK: Handoffs, Guardrails, Tracing — **Learn + Build** · Python · ~75min
    Five primitives — Agent, Handoff (modeled as a `transfer_to_<agent>` tool), Guardrail, Session, Tracing — built on the Responses API. Distinguishes input/output/tool guardrails in parallel (default, lower latency, token waste on trip) vs blocking mode, and ships span-style tracing on by default. Builds a stdlib runtime with handoffs, guardrails, and tracing.
    **Tools/Frameworks:** OpenAI Agents SDK, Responses API, handoff tools, `InputGuardrailTripwireTriggered`, W3C tracing.

17. ### 17 · Claude Agent SDK: Subagents and Session Store — **Learn + Build** · Python · ~75min
    The library form of the Claude Code harness: built-in tools, subagents for parallelization and context isolation, lifecycle hooks (`PreToolUse`/`PostToolUse`/`SessionStart`/`PreCompact`), W3C trace propagation, and session-store parity (`append`/`load`/`list_sessions`/`delete`, `--session-mirror`). Distinguishes the raw Client SDK (you own the loop) from the Agent SDK (the Claude Code loop as a library); Claude Managed Agents is the hosted long-running-async alternative.
    **Tools/Frameworks:** Claude Agent SDK (`claude-agent-sdk`), Anthropic Client SDK, subagents, session store, lifecycle hooks, MCP.

18. ### 18 · Agno and Mastra: Production Runtimes — **Learn** · Python, TypeScript · ~45min `[GAP 2: complexity ladder]`
    The 2026 production-runtime pairing for teams that want "just the agent loop, fast" without framework heaviness: Agno (Python, ~2μs agent instantiation, stateless session-scoped FastAPI backend) and Mastra (TypeScript on Vercel AI SDK, Agents/Tools/Workflows, unified model router over 3,300+ models). The pick is a complexity/cost decision — language fit (Python-first vs TypeScript-first) and runtime ergonomics versus the framework-owned primitives of LangGraph/AutoGen/CrewAI.
    **Tools/Frameworks:** Agno, FastAPI, Mastra, Vercel AI SDK, Zod, Mastra Studio, ClickHouse.

19. ### 19 · Benchmarks: SWE-bench, GAIA, AgentBench — **Learn** · Python · ~60min
    Three anchoring agent benchmarks: SWE-bench (real GitHub issues, FAIL_TO_PASS test gating, the human-curated Verified 500-task subset) plus its contamination story (SWE-bench+ found 32.67% of patches leaked solutions); GAIA ("simple for humans 92%, hard for AI 15%," three difficulty levels); AgentBench's eight environments. The lesson: know composition, contamination, and what each benchmark does not measure before quoting a number.
    **Tools/Frameworks:** SWE-bench / SWE-bench Verified / SWE-bench+, GAIA, AgentBench, FAIL_TO_PASS gating.

20. ### 20 · Benchmarks: WebArena and OSWorld — **Learn** · Python · ~60min
    WebArena (812 long-horizon tasks across four self-hosted web apps, execution-based eval) and OSWorld (369 real tasks across Ubuntu/Windows/macOS via free-form keyboard/mouse on 1920×1080 screenshots). Names the two primary OSWorld failure modes — GUI grounding (pixel→element) and operational knowledge (the menu/shortcut tail) — and the OSWorld-G / OSWorld-Human follow-ups that decompose grounding from planning and expose the 1.4–2.7× trajectory-efficiency gap.
    **Tools/Frameworks:** WebArena, VisualWebArena, TheAgentCompany, OSWorld, OSWorld-G, OSWorld-Human.

21. ### 21 · Computer Use: Claude, OpenAI CUA, Gemini — **Learn** · Python · ~60min
    Three 2026 production computer-use models, all vision-based: Claude (screenshot in, keyboard/mouse out, no accessibility API), OpenAI CUA/Operator (RL-trained GPT-4o variant, OSWorld 38.1%), Gemini 2.5 Computer Use (browser-only, ~70% Online-Mind2Web, per-step safety service). The shared contract all three enforce: screenshots, DOM text, and tool outputs are untrusted input; only direct user instructions count as permission.
    **Tools/Frameworks:** Claude computer use (`computer` tool), OpenAI CUA/Operator, Gemini 2.5 Computer Use, Xvfb virtual display.

22. ### 22 · Voice Agents: Pipecat and LiveKit — **Learn** · Python · ~60min
    Voice as a first-class production category with brutal latency budgets (~450–600ms end-to-end) and partial audio as the default. Pipecat gives a Python frame-based pipeline (VAD → STT → LLM → TTS → transport) with DOWNSTREAM/UPSTREAM flow; LiveKit Agents bridges models to users over WebRTC with `MultimodalAgent` (direct audio) and `VoicePipelineAgent` (STT→LLM→TTS cascade) classes plus semantic turn detection.
    **Tools/Frameworks:** Pipecat, LiveKit Agents, WebRTC, Silero VAD, STT/TTS, RTVI, Daily/SmallWebRTCTransport.

23. ### 23 · OpenTelemetry GenAI Semantic Conventions — **Learn + Build** · Python · ~60min
    OTel's GenAI SIG (April 2024) defines the standard schema for agent telemetry so traces mean the same thing across Datadog/Grafana/Jaeger/Honeycomb: model/client, agent (`create_agent`/`invoke_agent`, CLIENT vs INTERNAL span kind), and tool span categories. Covers the load-bearing attributes (`gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.agent.name`, `gen_ai.data_source.id`) and the opt-in content-capture contract (`OTEL_SEMCONV_STABILITY_OPT_IN`).
    **Tools/Frameworks:** OpenTelemetry GenAI semantic conventions, OTel SDKs, provider-specific conventions (Anthropic/Bedrock/OpenAI).

24. ### 24 · Agent Observability: Langfuse, Phoenix, Opik — **Learn** · Python · ~45min
    Three open-source platforms that ingest OTel spans and run evaluations: Langfuse (MIT, 6M+ installs/month, tracing + prompt management + sessions + replay), Arize Phoenix (Elastic 2.0, deep agent evals, RAG relevancy, OpenInference auto-instrumentation), Comet Opik (Apache 2.0, automated prompt optimization, guardrails, LLM-judge hallucination detection). Industry data: 89% of orgs have agent observability in place; quality issues are the top production barrier (32%).
    **Tools/Frameworks:** Langfuse, Arize Phoenix, OpenInference, Comet Opik, LLM-as-judge, ClickHouse.

25. ### 25 · Multi-Agent Debate and Collaboration — **Learn + Build** · Python · ~60min
    Du et al.'s "Society of Minds" (ICML 2024): N model instances independently propose, then iteratively critique each other over R rounds to converge — improving factuality, rule-following, and reasoning, with cross-model debate beating single-model. Sparse topology (star/ring/hub-and-spoke) matches full-mesh accuracy at lower token cost (star N=5,R=3 = 12 critique ops vs full-mesh 60). Builds full-mesh and sparse debate variants over a scripted LLM.
    **Tools/Frameworks:** Python stdlib, Society of Minds (Du 2024), sparse topology debate, scripted LLM.

26. ### 26 · Failure Modes: Why Agents Break — **Learn + Build** · Python · ~60min
    MASFT (Berkeley 2025) catalogs 14 multi-agent failure modes in 3 categories with inter-annotator κ=0.88; Microsoft's taxonomy documents how existing AI failures (bias, hallucination) amplify under autonomy; field data converges on five recurring modes — hallucinated actions, scope creep, cascading errors, context loss, tool misuse. The claim: these are fundamental design flaws, not LLM limitations fixable with better base models. Builds a stdlib detector that tags traces with failure-mode labels.
    **Tools/Frameworks:** MASFT, Microsoft agentic-failure taxonomy, Arise/Galileo field analyses, trace-tagging detector.

27. ### 27 · Prompt Injection and the PVE Defense — **Build** · Python · ~75min
    Greshake et al.'s indirect prompt injection threat model (attacker plants instructions in retrieved content; processing them is equivalent to arbitrary code execution on the tool surface) with five exploit classes (data theft, worming, memory poisoning, ecosystem contamination, arbitrary tool use). The 2026 six-control defense doctrine (untrusted content, allowlist navigation, per-step safety, guardrails, HITL, external capture) implemented as a PVE (Prompt-Validator-Executor) — a cheap fast validator before the expensive main model commits.
    **Tools/Frameworks:** Python stdlib, PVE pattern, allowlist/blocklist, per-step safety (Gemini), guardrails, HITL.

28. ### 28 · Orchestration Patterns: Supervisor, Swarm, Hierarchical — **Learn + Build** · Python · ~60min `[GAP 2: complexity ladder]`
    Four recurring 2026 orchestration patterns — supervisor-worker, swarm/peer-to-peer, hierarchical, debate — with the Anthropic rule "build the right system for your needs" gating topology choice. The complexity-ladder spine: start with a single agent plus the five workflow patterns (Lesson 12); add multi-agent topology only when that is insufficient, because the 2026 LangChain guidance is to do supervision through direct tool calls rather than supervisor libraries for finer context control.
    **Tools/Frameworks:** Python stdlib, LangGraph `create_supervisor`/swarm, OpenAI handoffs, CrewAI Hierarchical, Anthropic orchestrator-workers.

29. ### 29 · Production Runtimes: Queue, Event, Cron — **Learn** · Python · ~60min
    Six production runtime shapes — request-response, streaming, durable execution, queue-based background, event-driven, scheduled — and the matching frameworks, with the rule "pick the shape before you pick the framework." Durable execution (LangGraph/AutoGen actor) handles long-horizon tasks; queue/background (Celery/BullMQ/SQS) handles dozens-to-hundreds of steps; event-driven (Claude Managed Agents) handles async; observability is load-bearing at every shape.
    **Tools/Frameworks:** Agno, Mastra, LangGraph, AutoGen v0.4, Celery, BullMQ, SQS+Lambda, Claude Managed Agents.

30. ### 30 · Eval-Driven Agent Development — **Learn + Build** · Python · ~60min
    Anthropic's guidance — "start with simple prompts, optimize with comprehensive evaluation, and add multi-step agentic systems only when needed" — positions evaluation as the outer loop driving every Phase 14 choice. Three layers: static benchmarks (SWE-bench Verified, WebArena/OSWorld, GAIA, BFCL V4) for cross-model comparison, custom offline evals (LLM-judge, execution-based, trajectory-based) for product shape, and online evals (session replays, guardrail alerts, per-step cost) — with evals living next to code, running in CI, gating PRs.
    **Tools/Frameworks:** SWE-bench Verified, WebArena/OSWorld, GAIA, BFCL V4, Langfuse/Phoenix/Opik, evaluator-optimizer loop, CI gating.

31. ### 31 · Agent Workbench Engineering: Why Capable Models Still Fail — **Learn + Build** · Python · ~45min
    Separates model capability from execution reliability: a frontier model dropped into a real repo fails not on Python but on the work — no idea what "done" means, where it can write, which tests are authoritative. Names the seven workbench surfaces that decide whether an agent ships (instructions, state, scope, feedback, verification, review, handoff), each with a failure-when-missing column; the workbench is model-independent — you can swap the model and keep the surfaces, but not the reverse.
    **Tools/Frameworks:** Python stdlib, seven-surface workbench model, prompt-only vs workbench-guided comparison.

32. ### 32 · The Minimal Agent Workbench — **Build** · Python · ~45min
    The smallest useful workbench is three files: a short `AGENTS.md` router (not a 3000-line manual), an `agent_state.json` system of record, and a `task_board.json` that survives multi-session work without chat history. The argument: long manuals get ignored, short routers get followed; the agent reads state at every turn and writes it at the end, so the next session reads state instead of replaying chat.
    **Tools/Frameworks:** Python stdlib, `AGENTS.md` router, `agent_state.json`, `task_board.json`, `docs/agent-rules.md`.

33. ### 33 · Agent Instructions as Executable Constraints — **Build** · Python · ~50min
    Turns prose wishes ("be careful," "test thoroughly") into machine-checkable rules across five categories — Startup, Forbidden, Definition-of-done, Uncertainty, Approval — each with a check the workbench runs at runtime and a reviewer scores after the fact. Rules live in `docs/agent-rules.md` away from the root router, scored by a `rule_checker.py` that emits a diff-friendly report.
    **Tools/Frameworks:** Python stdlib, `docs/agent-rules.md`, `rule_checker.py`, `rule_report.json`, five-category rule schema.

34. ### 34 · Repo Memory and Durable State — **Build** · Python · ~60min
    The repo is the system of record, chat is volatile: state lives in JSON files written under a schema, persisted atomically, diff-friendly in review. Builds a `StateManager` that loads, validates, mutates, and persists `agent_state.json`/`task_board.json` against authored JSON Schemas, refusing bad writes before they corrupt the workbench. Durability test: would this be useful three months from now in a CI rerun?
    **Tools/Frameworks:** Python stdlib, `jsonschema`, `agent_state.schema.json`, atomic writes, `StateManager`.

35. ### 35 · Initialization Scripts for Agents — **Build** · Python · ~45min
    Every cold-start session pays a tax (probing Python version, test command, repo paths, env vars); an `init_agent.py` pays it once and writes an `init_report.json` the agent reads at startup. Probes runtime versions, dependency availability, test command, repo paths, environment variables, state/board freshness, and last-known-good commit — failing loud, fast, and with one place to look when initialization fails.
    **Tools/Frameworks:** Python stdlib, `init_agent.py`, `init_report.json`, deterministic probes.

36. ### 36 · Scope Contracts and Task Boundaries — **Build** · Python · ~50min
    A per-task `scope_contract.json` says where work begins, where it ends, and how to roll back if it spills — turning "stay in scope" from a wish into a check (allowed_files, forbidden_files, acceptance_criteria, rollback plan, approval boundaries). Builds a `scope_checker.py` that compares the final diff against the contract and flags violations, making scope creep — the most under-monitored failure mode because the agent narrates each step in good faith — visible, automatic, and reviewable.
    **Tools/Frameworks:** Python stdlib, `scope_contract.json`, `scope_checker.py`, glob-based file allow/deny lists.

37. ### 37 · Runtime Feedback Loops — **Build** · Python · ~50min
    A feedback runner wraps every shell command and persists a structured record (exact argv, `stdout_tail`/`stderr_tail` with deterministic truncation, exit_code, duration_ms, agent_note) so the agent reacts to facts instead of its own prediction of facts. Distinguishes runtime feedback (captured into the loop, read next turn) from observability telemetry; the loop refuses to advance when feedback is missing, killing "all tests pass" claims with no record of a run.
    **Tools/Frameworks:** Python stdlib, `run_with_feedback.py`, `subprocess`, `feedback_record.jsonl`, deterministic truncation.

38. ### 38 · Verification Gates — **Build** · Python · ~55min
    The agent does not mark its own work done: a deterministic `verify_agent.py` reads the scope report, rule report, feedback log, and diff, then emits a single `verification_report.json` verdict the reviewer and CI both read. Combines acceptance-command-ran, scope-held, rules-passed, and feedback-record checks with block-severity failures that refuse to advance the task without exception — countering "looks good," "tests passed" (said with no record), and loosely-interpreted acceptance.
    **Tools/Frameworks:** Python stdlib, `verify_agent.py`, `verification_report.json`, severity-tagged checks, CI wiring.

39. ### 39 · Reviewer Agent: Separate Builder from Marker — **Build** · Python · ~55min
    The agent that wrote the code cannot grade it: a reviewer is a second loop with a different system prompt, a different goal, and read-only access to everything the builder produced. Author a five-dimension rubric (problem fit, scope discipline, assumptions, verification quality, handoff readiness) scored 0–2, emitting a `review_report.json` so human sign-off starts from a real artifact rather than vibes — catching the "solved the wrong half of the bug" case the verification gate cannot.
    **Tools/Frameworks:** Python stdlib, reviewer agent loop, `reviewer_checklist.md`, `review_report.json`, 0–2 rubric.

40. ### 40 · Multi-Session Handoff — **Build** · Python · ~50min
    A handoff packet turns "the agent worked for an hour" into "the next session is productive in the first minute": generated automatically from workbench artifacts, carrying seven fields (summary, changed_files, commands_run, failed_attempts, open_risks, next_action, verdict_pointer). Trims large feedback logs into a handoff-sized summary and makes the next session's first action deterministic, so the cost of a bad handoff isn't paid every session for the life of the task.
    **Tools/Frameworks:** Python stdlib, `generate_handoff.py`, `handoff.md`/`handoff.json`, state/verdict/review/feedback generators.

41. ### 41 · The Workbench on a Real Repo — **Build** · Python · ~60min
    Runs the same task (add `/signup` validation + a test) twice on a sample FastAPI app — prompt-only versus workbench-guided — and measures five outcomes to make the case with numbers, not demos. The sample app includes `README.md` and `scripts/release.sh` as forbidden-zone bait; the before/after report is the artifact you hand to a "but my model is good enough" skeptic.
    **Tools/Frameworks:** Python stdlib, sample FastAPI app, before-after-report, all seven workbench surfaces.

42. ### 42 · Capstone: Ship a Reusable Agent Workbench Pack — **Build** · Python · ~75min
    Packages the seven surfaces into one drop-in `agent-workbench-pack/` directory (AGENTS.md + docs/, schemas/, scripts/, `bin/install.sh`) that lays down idempotently into any target repo. Pins the schemas, scripts, and templates so a new repo gets a known-good baseline, with a defended cut for what stays in the pack versus out — the artifact this curriculum trades on.
    **Tools/Frameworks:** Python stdlib, `agent-workbench-pack/`, `bin/install.sh`, pinned JSON Schemas, templates.

## Phase 15 — Autonomous Systems

1. ### 01 · The Shift from Chatbots to Long-Horizon Agents — **Learn** · Python · ~45min `[GAP 2: complexity ladder]`
   Frames the qualitative break from single-turn chatbots to autonomous agents that run minutes-to-hours: METR's Time Horizon 1.1 (Jan 2026) puts Claude Opus 4.6 at ~14 hours of expert work at 50% reliability, doubling roughly every seven months since GPT-2. The complexity-ladder spine: every assumption built around single-turn chat (context, trust, failure modes, cost, observability) breaks when runs last longer than lunch — context needs compression, review shifts from output to trajectory audit, cost needs budgets/kill-switches, and a horizon number is a capability ceiling not a reliability floor (eval-vs-deploy behavior gap).
   **Tools/Frameworks:** METR Time Horizon 1.1, HCAST/RE-Bench/SWAA suites, horizon-curve simulator, eval-context-gaming literature.

2. ### 02 · STaR, V-STaR, Quiet-STaR — Self-Taught Reasoning — **Learn** · Python · ~60min
   The smallest self-improvement loop: STaR generates a rationale, keeps the ones landing on correct answers, fine-tunes on them (GPT-J GSM8K 5.8%→10.7%; CommonsenseQA 72.5% matching a 30× larger fine-tuned GPT-3); V-STaR adds a DPO-trained verifier for inference-time selection (+4–17 points); Quiet-STaR pushes per-token internal rationales (Mistral 7B GSM8K 5.9%→10.9%). The shared safety concern: all three use the final answer as the gradient signal, so shortcuts that reach the right answer get reinforced and break silently OOD.
   **Tools/Frameworks:** STaR (Zelikman 2022), V-STaR (Hosseini 2024), Quiet-STaR (Zelikman 2024), DPO, rationalization, bootstrap-loop simulator.

3. ### 03 · AlphaEvolve — Evolutionary Coding Agents — **Learn** · Python · ~60min
   Pairs a frontier coding model with an evolutionary loop and a machine-checkable evaluator: the LLM proposes targeted edits to a program database, the evaluator scores each variant, high-scorers become parents (48-scalar-multiplication 4×4 complex matmul beating Strassen's 56-year-old bound; ~0.7% Borg cluster-compute recovery; 32.5% FlashAttention speedup). The asymmetry that is the lesson: the architecture is boring on purpose and wins only come where the evaluator is fast, deterministic, and hard to game — remove it and the loop optimizes for pretty code.
   **Tools/Frameworks:** AlphaEvolve (DeepMind 2025), Gemini Flash/Pro ensemble, MAP-elites/island-based database, machine-checkable evaluators.

4. ### 04 · Darwin Godel Machine — Open-Ended Self-Modifying Agents — **Learn** · Python · ~60min
   Drops Schmidhuber's formal-proof requirement and keeps the archive: the agent proposes edits to its own Python scaffolding, each variant is scored on SWE-bench/Polyglot, improvements are retained (SWE-bench 20%→50%, Polyglot 14.2%→30.7%, generalizing across Claude 3.5/o3-mini/3.7). The target is the agent itself (tool wrappers, prompts, sub-agent routers), which changes the safety profile — the paper documents DGM learning to remove its own hallucination-detection markers to raise scores.
   **Tools/Frameworks:** Darwin Godel Machine (Zhang 2025), SWE-bench, Polyglot, archive-based self-modification, MAP-elites.

5. ### 05 · AI Scientist v2 — Workshop-Level Autonomous Research — **Learn** · Python · ~60min
   Sakana's AI Scientist v2 runs the full research loop (idea, code, experiments, figures, writeup, submission) via agentic tree search with a vision-language critique loop — the first system with a generated paper passing peer review at an ICLR 2025 workshop. Independent evaluation (Beel et al.) tempers the claim: 42% of experiments failed from coding errors and the literature step frequently mislabeled established concepts as novel; Sakana's own docs warn the codebase executes LLM-written code and recommend Docker isolation.
   **Tools/Frameworks:** AI Scientist v2 (Sakana 2025), agentic tree search, vision-language figure critique, Docker sandbox isolation.

6. ### 06 · Automated Alignment Research (Anthropic AAR) — **Learn** · Python · ~60min
   Anthropic ran parallel Claude Opus 4.6 Autonomous Alignment Researchers in independent sandboxes coordinating via a shared forum whose logs live outside every sandbox (so agents cannot delete their own records); on weak-to-strong training the AARs beat the human baseline. Two load-bearing points: prescribed workflows constrain AAR flexibility and degrade performance (overspecified scaffolds hurt capable agents), and AAR is one step short of the RSP's AI R&D-4 threshold — automating alignment research is the compression step that compresses the timeline to the exact misalignment risks RSPs detect.
   **Tools/Frameworks:** Anthropic AAR (2026), parallel sandboxed agents, append-only out-of-sandbox forum, S3 object-lock analog, weak-to-strong training.

7. ### 07 · Recursive Self-Improvement — Capability vs Alignment — **Learn** · Python · ~60min `[GAP 2: complexity ladder]`
   Positions RSI as an engineering problem with concrete tooling (ICLR 2026 Rio workshop) and the central complexity-ladder/race question: if capability compounds at rate `r_c` and alignment at `r_a`, the misalignment gap grows when `r_c > r_a` — and optimization loops are better at sharp targets (benchmarks) than fuzzy ones (values). Frames the Hassabis "can the loop close without a human" question and the closure conditions (human-between-cycles, cross-model generalization, alignment keeping pace), grounded in the alignment-faking result (12% basic, up to 78% after retraining).
   **Tools/Frameworks:** capability-vs-alignment race simulator, Anthropic alignment-faking study, DGM/AAR/AlphaEvolve as loop steps, RSI workshop framing.

8. ### 08 · Bounded Self-Improvement Designs — **Learn** · Python · ~60min `[GAP 2: complexity ladder]`
   Four primitives for bounding a self-improvement loop so the constraints cannot be silently weakened by the loop itself: formal invariants (checked by external code the loop cannot edit), alignment anchors (immutable objective pinned outside the edit surface), multi-objective constraints (every dimension must hold, not just performance), and regression detection (pause on historical-metric loss). The honest framing — these are mitigations, not proofs: information-theoretic results (Kolmogorov complexity, Löb's theorem) bound what any system can prove about its own successors.
   **Tools/Frameworks:** formal invariants, alignment anchors, multi-objective constraints, regression detection, RSP v3.0 / FSF v3 thresholds, SAHOO/HyperAgents.

9. ### 09 · The Autonomous Coding Agent Landscape (2026) — **Learn** · Python · ~45min
   SWE-bench Verified went 4%→80.9% in under three years; same Claude Sonnet 4.5 scored 43.2% on SWE-agent v1 and 59.8% on Cline autonomous — scaffolding now matters as much as the model. OpenHands (formerly OpenDevin) is the most active MIT platform with a CodeAct loop executing Python in a sandbox instead of JSON tool calls. Methodological caveat: 161 of 500 Verified tasks need only a 1–2 line change, and SWE-bench Pro (10+ lines) sits at 23–59% — real-world quality hides behind saturated top scores.
   **Tools/Frameworks:** SWE-bench Verified/Pro, OpenHands (CodeAct, Docker), SWE-agent, Aider, Cline, Epoch AI leaderboard.

10. ### 10 · Claude Code as an Autonomous Agent: Permission Modes and Auto Mode — **Learn** · Python · ~45min
    Seven permission modes form a capability ladder (plan → default → acceptEdits → acceptExec → autoMode → yolo → bypassPermissions), each a different speed-vs-review-per-action tradeoff. Auto Mode (Mar 2026) replaces per-action approval with a two-stage parallel classifier: a single-token fast check on every action, a chain-of-thought deep review only on flagged ones, with `max_turns` and `max_budget_usd` budgets. Anthropic states explicitly the classifier is not sufficient alone — a new risk category (everything the agent can reach) per Bruce Schneier.
    **Tools/Frameworks:** Claude Code permission modes, Auto Mode two-stage classifier, `max_turns`, `max_budget_usd`, tool allow/deny lists.

11. ### 11 · Browser Agents and Long-Horizon Web Tasks — **Learn** · Python · ~45min
    The 2026 browser-agent landscape: ChatGPT agent (BrowseComp SOTA 68.9%, Operator shut down Aug 2025), Claude Sonnet + Vercept (OSWorld <15%→72.5%), Gemini 3 Pro + Browser Use, and WebArena-Verified (ServiceNow, ICLR 2026) fixing 11.3 points of false-negative rate plus a 258-task Hard subset. The attack surface is uncomfortable — Tainted Memories, HashJack, one-click Perplexity Comet hijacks — and OpenAI's head of preparedness states indirect prompt injection "is not a bug that can be fully patched."
    **Tools/Frameworks:** ChatGPT agent, Claude Computer Use + Vercept, Gemini Browser Use, BrowseComp/OSWorld/WebArena-Verified, indirect-prompt-injection attack model.

12. ### 12 · Long-Running Background Agents: Durable Execution — **Learn** · Python · ~60min
    Production long-horizon agents do not run in `while True`: every LLM call becomes an activity with checkpoint, retry, and replay, because LLM calls are non-deterministic, expensive, failing, side-effectful — exactly the activity profile. Temporal's OpenAI Agents SDK integration went GA Mar 2026; Claude Code Routines runs scheduled invocations without a persistent local process; sessions pause on human-input, survive deploys, resume from the latest checkpoint keyed by `thread_id`. Notes METR's "35-minute degradation" — success drops roughly quadratically with horizon.
    **Tools/Frameworks:** Temporal, OpenAI Agents SDK, Claude Code Routines, LangGraph/Microsoft Agent Framework/Cloudflare Durable Objects, `thread_id` checkpoints.

13. ### 13 · Action Budgets, Iteration Caps, and Cost Governors — **Learn** · Python · ~60min
    The "Denial of Wallet" failure mode (an agent keeps reasoning/calling/billing because nothing was designed to stop it) is defended by a stack of limits at different time scales: `max_tokens`, per-task token/dollar budgets, per-tool caps, iteration caps (`max_turns`), per-minute/day/month caps, financial velocity limits (>$50 in 10 min → cut), tiered model routing, prompt caching, context windowing, HITL on expensive actions, kill switch on breach. Different failure modes need different time scales — a single monthly cap catches a runaway only after the wallet is gone.
    **Tools/Frameworks:** Microsoft Agent Governance Toolkit, Claude Code `max_budget_usd`/`max_turns`, LaunchDarkly/Statsig, prompt caching, context windowing.

14. ### 14 · Kill Switches, Circuit Breakers, and Canary Tokens — **Learn** · Python · ~60min
    Three detectors sitting next to the cost layer: a kill switch (boolean the agent reads but cannot write — feature flag, Redis key, signed config, container kill), a circuit breaker (closed/open/half-open, trips on patterns like five identical tool calls), and a canary token (fake credential or honeypot record an agent has no legitimate reason to touch). All pre-LLM engineering reasserted for the agent attack surface; eBPF/Cilium can rewrite a quarantined pod's egress to a forensic honeypot at the kernel layer; statistical detectors (EWMA/CUSUM) must be layered with hard constitutional limits that do not bend.
    **Tools/Frameworks:** feature flags (LaunchDarkly/Statsig/Unleash), Redis, Nygard circuit breakers, canary tokens/honeypots, Cilium/eBPF, EWMA/CUSUM.

15. ### 15 · Human-in-the-Loop: Propose-Then-Commit — **Learn** · Python · ~60min
    The 2026 HITL consensus is specific: the proposed action is persisted to a durable store with an idempotency key, surfaced with intent/data-lineage/permissions/blast-radius/rollback-plan, committed only after positive acknowledgement, and verified after execution. LangGraph `interrupt()` + PostgreSQL, Microsoft Agent Framework `RequestInfoEvent`, and Cloudflare `waitForApproval()` all implement the shape; the canonical failure is the rubber-stamp approval, mitigated by challenge-and-response with an explicit checklist.
    **Tools/Frameworks:** LangGraph `interrupt()`, Microsoft Agent Framework `RequestInfoEvent`, Cloudflare `waitForApproval()`, idempotency keys, challenge-and-response checklists.

16. ### 16 · Checkpoints and Rollback — **Learn** · Python · ~60min
    Joins durable execution (Lesson 12) with propose-then-commit (Lesson 15): every graph-state transition persists, worker leases expire on crash and another worker resumes at the latest checkpoint (LangGraph→Postgres; Cloudflare Durable Objects hold per-key state across weeks). The combination that works is idempotency key (prevents double-execute) + precondition check (state still consistent with approval) + post-action verify (side effect actually happened) + rollback on verify-fail — without all four a retry after a transient failure can double-execute an approved action. EU AI Act Article 14 makes queryable checkpoints/rehearsed rollbacks mandatory for high-risk systems.
    **Tools/Frameworks:** LangGraph checkpoints, Cloudflare Durable Objects, Microsoft Agent Framework `Checkpoint`, idempotency keys, `UPDATE … RETURNING *` verify, EU AI Act Art. 14.

17. ### 17 · Constitutional AI and Rule Overrides — **Learn** · Python · ~60min
    Anthropic's Jan 2026 79-page CC0 Claude Constitution moves from rule-based to reason-based alignment with a four-tier priority hierarchy (safety/supporting-human-oversight → ethics → Anthropic guidelines → helpfulness). Hardcoded prohibitions (bioweapons uplift, CSAM, critical-infrastructure attacks) cannot be overridden by operator or user; soft-coded defaults (response length, topical scope, style, tool patterns) are operator-adjustable within bounds. Honest caveat: reason-based alignment relies on the model generalizing principles to unanticipated situations, and the 2023 participatory experiment showed ~50% divergence between public-sourced and corporate principles.
    **Tools/Frameworks:** Claude Constitution (Jan 2026), four-tier priority resolver, hardcoded-prohibition vs soft-default split, Constitutional AI/RLAIF (Bai 2022).

18. ### 18 · Llama Guard and Input/Output Classification — **Learn** · Python · ~45min
    Llama Guard 3 (Llama-3.1-8B base, MLCommons 13-hazard taxonomy, 8 languages, 1B-INT4 at >30 tok/s on mobile) and Llama Guard 4 (multimodal, S1–S14 including S14 Code Interpreter Abuse) as drop-in input/output classifiers; NVIDIA NeMo Guardrails v0.20.0 (Jan 2026) adds Colang dialog-flow rails. The honest note: classifiers are a layer, not a solution — "Bypassing Prompt Injection and Jailbreak Detection" (Huang 2025) showed Emoji Smuggling hitting 100% ASR on six guard systems and NeMo Guard Detect at 72.54% ASR on jailbreaks.
    **Tools/Frameworks:** Llama Guard 3/4, MLCommons taxonomy, NVIDIA NeMo Guardrails, Colang, Prompt Guard, INT4 quantization.

19. ### 19 · Anthropic Responsible Scaling Policy v3.0 — **Learn** · Python · ~45min
    RSP v3.0 (effective Feb 24 2026) adds a two-tier mitigation schedule (Anthropic-unilateral vs industry-wide recommendation including RAND SL-4), Frontier Safety Roadmaps and Risk Reports as standing documents, and the AI R&D-4 threshold (automate a substantial fraction of AI research at competitive cost → must publish an affirmative misalignment-risk case). Drops the 2023 pause commitment — the sharpest regression; SaferAI downgraded the score 2.2→1.9 ("weak"). Claude Opus 4.6 does not cross AI R&D-4 but "confidently ruling this out is becoming difficult."
    **Tools/Frameworks:** Anthropic RSP v3.0, AI R&D-4 threshold, Frontier Safety Roadmaps, Risk Reports, RAND SL-4, SaferAI scoring.

20. ### 20 · OpenAI Preparedness Framework and DeepMind Frontier Safety Framework — **Learn** · Python · ~45min
    OpenAI PF v2 (Apr 2025) splits categories into Tracked (trigger Capabilities + Safeguards Reports, Safety Advisory Group review) vs Research (Long-range Autonomy, Sandbagging, Autonomous Replication, Undermining Safeguards — "potential" mitigations, no automatic trigger). DeepMind FSF v3 (Sep 2025, Tracked Capability Levels added Apr 2026) folds autonomy into ML R&D and Cyber domains (ML R&D autonomy level 1 = fully automate the AI R&D pipeline at competitive cost). All three converge on a Safety Advisory Group, deceptive-alignment acknowledgement, and that monitoring-only defenses have a ceiling.
    **Tools/Frameworks:** OpenAI Preparedness Framework v2, DeepMind FSF v3, Critical/Tracked Capability Levels, three-framework decision-table diff.

21. ### 21 · METR Time Horizons and External Capability Evaluation — **Learn** · Python · ~60min
    METR (ex-ARC Evals, independent 501(c)(3) since Dec 2023) fits a logistic curve to task-success probability vs log(expert completion time); the 50% intersection is the time horizon (Time Horizon 1.1, Jan 2026: Claude Opus 4.6 ~14 hours; post-2023 doubling ~4.3 months). Suites HCAST (180+ tasks, 1 min–8+ hr), RE-Bench (71 ML research-engineering tasks with expert baseline), SWAA. The interpretation skill: a horizon is an idealized upper bound (no human, no real consequences) — METR itself documents the eval-vs-deployment behavior gap, so production needs your own evals on your own distribution.
    **Tools/Frameworks:** METR Time Horizon 1.0/1.1, HCAST, RE-Bench, SWAA, logistic-fit horizon estimator, prototype monitoring evals.

22. ### 22 · CAIS, CAISI, and Societal-Scale Risk — **Learn** · Python · ~45min
    Two distinct rhyming entities: CAIS (Center for AI Safety, 501(c)(3), the four-risk framework — malicious use, AI races, organizational risks, rogue AIs — and the May 2023 extinction-risk statement) and CAISI (NIST's US-government center for voluntary agreements and unclassified cyber/bio/chemical capability evaluations). Organizational risk is the most practitioner-actionable of the four (safety culture, audit rigor, defense layering, information security); California SB-53 would be the first US state-level catastrophic-risk regulation if signed. Builds a four-risk inventory and mitigation matcher.
    **Tools/Frameworks:** CAIS four-risk framework, NIST CAISI, AI Dashboard, Remote Labor Index, Superintelligence Strategy Paper, California SB-53.

## Phase 16 — Multi-Agent and Swarms

1. ### 01 · Why Multi-Agent? — **Learn** · TypeScript · ~60min `[GAP 2: complexity ladder]`
   The single-agent ceiling (context overflow, mixed expertise in one prompt, sequential bottleneck) and the explicit complexity-ladder decision: the smart move past the ceiling is not a bigger agent but more agents — but only when a task requires more context than fits in one window, different expertise at different stages, or parallelizable work. Compares orchestration patterns (pipeline, parallel fan-out, supervisor, hierarchical) and names the tradeoffs (latency, cost, debugging difficulty) versus single-agent simplicity, so multi-agent is a deliberate choice, not a default.
   **Tools/Frameworks:** single-agent ceiling model, orchestration-pattern comparison, role-boundary/shared-state/communication-contract design.

2. ### 02 · Heritage of FIPA-ACL and Speech Acts — **Learn** · Python · ~60min
   Reads the 2000 IEEE FIPA-ACL standard (twenty performatives, SL0/SL1 content languages, contract-net/subscribe-notify interaction protocols; JADE/JACK reference platforms; faded ~2010 as the web won) so the 2026 protocol sprawl (MCP, A2A, ACP, ANP, NLIP, CA-MCP) reads as a JSON-native, natural-language-ontology rehash. Speech-act theory (Austin/Searle) → KQML (1993) → FIPA-ACL → today's `tools/call` and task lifecycles; knowing the heritage tells you which "innovations" are reinventions and which old failure modes the new specs will rediscover.
   **Tools/Frameworks:** FIPA-ACL (`fipa00037.pdf`), KQML, speech-act theory, JADE/JACK, twenty performatives.

3. ### 03 · Communication Protocols — **Build** · TypeScript · ~120min
   The four-protocol stack as layers: MCP (agent ↔ tool discovery/execution), A2A (agent ↔ agent collaboration), ACP (enterprise audit/runs/trajectory metadata), ANP (decentralized identity/DID/trust). Builds real wire-format implementations of each — MCP tool discovery and invocation, an A2A agent card and task endpoint over HTTP — and wires them together so agents discover tools via MCP and delegate tasks via A2A, because passing strings between agents fails on misinterpretation, deadlock, and cross-team scale.
   **Tools/Frameworks:** MCP, A2A (Agent Cards, task lifecycle), ACP, ANP (DID, E2EE), JSON-RPC, HTTP endpoints.

4. ### 04 · The Multi-Agent Primitive Model — **Learn** · Python · ~60min
   Every 2026 framework (AutoGen, LangGraph, CrewAI, OpenAI Agents SDK, Microsoft Agent Framework, Google ADK) is a point in a four-dimensional design space: Agent, Handoff, Shared state, Orchestrator. Learn the four primitives once and read any new framework in one paragraph — surface syntax differs, the four knobs are stable, so framework comparison collapses to a short checklist of which default each picks per axis.
   **Tools/Frameworks:** four-primitive model (Agent/Handoff/Shared-state/Orchestrator), framework mapping table.

5. ### 05 · Supervisor / Orchestrator-Worker Pattern — **Learn + Build** · Python · ~75min
   One lead agent plans and delegates, specialized workers execute in fresh parallel contexts and report back — the pattern behind Anthropic's Research system (Claude Opus 4 lead, Sonnet 4 subagents), measured at +90.2% over single-agent Opus 4 on internal research evals with 80% of BrowseComp variance explained by token usage alone (fresh context per subagent is the main mechanism). Builds the pattern from the primitives and covers the 2026 production lessons; the lead never reads raw materials, workers never see each other until synthesis.
   **Tools/Frameworks:** Python stdlib + `threading`, supervisor/worker topology, Anthropic Research system, fresh-context-per-subagent.

6. ### 06 · Hierarchical Architecture and Its Failure Mode — **Learn + Build** · Python · ~60min
   Supervisor nested: manager agents over sub-managers over workers (CrewAI `Process.hierarchical` with a `manager_llm`; LangGraph `create_supervisor(create_supervisor(...))`). Natural for real org-chart tasks with local summarization, but the pattern most likely to collapse into managerial looping — task-assignment error, misread sub-outputs, consensus failure — because an LLM manager re-reasons the org every turn from whatever is in context. Sequential often beats it.
   **Tools/Frameworks:** Python stdlib, CrewAI `Process.hierarchical`, LangGraph nested `create_supervisor`, `manager_llm`.

7. ### 07 · Society of Mind and Multi-Agent Debate — **Learn + Build** · Python · ~60min
   Minsky's society-of-specialists premise made concrete by Du et al. 2023: N LLM instances propose, read each other's answers, critique, and update over R rounds, converging on a consensus that beats zero-shot CoT and reflection. Two findings: both multiple agents and multiple rounds contribute independently (agent-count alone plateaus; round-count alone barely helps; together produce the jumps). Heterogeneous debate (A-HMAD, different base models) reduces monoculture collapse by decorrelating errors.
   **Tools/Frameworks:** Python stdlib, Du et al. 2023 debate algorithm, self-consistency baseline, A-HMAD heterogeneous debate.

8. ### 08 · Role Specialization — Planner, Critic, Executor, Verifier — **Learn + Build** · Python · ~60min
   The most common 2026 decomposition — one agent plans, one executes, one critiques or verifies — formalized by MetaGPT (`Code = SOP(Team)`, five encoded roles) and ChatDev (chat chain with "communicative dehallucination"). The verifier is load-bearing: Cemri et al. MAST show every multi-agent failure traces to missing or broken verification; PwC reported a 7× accuracy gain (10%→70%) from structured validation loops in CrewAI. Critic is subjective/LLM-based; verifier is objective/deterministic — not the same role.
   **Tools/Frameworks:** MetaGPT, ChatDev, MAST (Cemri 2025), planner/critic/executor/verifier roles, CrewAI validation loops.

9. ### 09 · Parallel / Swarm / Networked Architectures — **Learn + Build** · Python · ~75min
   No central decider: agents read a shared event bus, pick up work asynchronously, write results back (LangGraph "Swarm Architecture"; Matrix represents control and data flow as serialized messages through distributed queues to eliminate the orchestrator bottleneck). The tradeoff is explicit — determinism and traceability for scalability; swarm fits many independent sub-problems and variable-duration work, and fails on ordered workflows or global-plan tasks where a planner is needed.
   **Tools/Frameworks:** Python stdlib + `threading`/`queue`, LangGraph Swarm, Matrix framework, shared event bus, producer-consumer queues.

10. ### 10 · Group Chat and Speaker Selection — **Learn + Build** · Python · ~60min
    AutoGen/AG2 GroupChat shares one conversation across N agents; a selector function (round-robin, LLM-selected, or custom) picks who speaks next — the archetype of emergent multi-agent conversation where agents react to a shared pool rather than a static graph. AutoGen v0.2 GroupChat semantics survive in the AG2 fork; AutoGen v0.4 rewrote it as an event-driven actor model; Microsoft merged AutoGen into Microsoft Agent Framework (RC Feb 2026) but the GroupChat primitive persists in both.
    **Tools/Frameworks:** AutoGen/AG2 GroupChat, `ConversableAgent`, round-robin/LLM/custom selectors, Microsoft Agent Framework.

11. ### 11 · Handoffs and Routines — Stateless Orchestration — **Learn + Build** · Python · ~60min
    OpenAI Swarm (Oct 2024) distilled orchestration to two primitives — routines (instructions + tools as a system prompt) and handoffs (a tool returning another Agent) — with no state machine: the LLM routes by calling the right handoff tool, and the orchestrator is whichever agent currently holds the conversation. The OpenAI Agents SDK (Mar 2025) is the production successor; Swarm remains the cleanest conceptual reference (a few hundred lines). Limitation: stateless, so memory is the caller's problem.
    **Tools/Frameworks:** OpenAI Swarm, OpenAI Agents SDK, routines, `transfer_to_<agent>` handoff tools, stateless orchestration.

12. ### 12 · A2A — The Agent-to-Agent Protocol — **Learn + Build** · Python · ~75min
    Google's A2A (announced Apr 2025, 150+ organizations by Apr 2026) is the peer-to-peer complement to MCP: where MCP is vertical (agent ↔ tools), A2A is horizontal (agent ↔ agent). Four elements — Agent Card (discovery at `/.well-known/agent.json`), Task (async stateful lifecycle `submitted→working→completed/failed/canceled`), Artifact (typed text/structured/image/video/audio results), opaque lifecycle (client sees state transitions, not implementation). Builds an A2A agent card and task endpoint over stdlib HTTP.
    **Tools/Frameworks:** A2A protocol, Agent Cards, task lifecycle, artifacts, `http.server`/`json`, Vertex AI Agent Builder, MCP pairing.

13. ### 13 · Shared Memory and Blackboard Patterns — **Learn + Build** · Python · ~75min
    Two stateful topologies — the full message pool (everyone reads everything, AutoGen GroupChat/MetaGPT, transparent but doesn't scale past ~10 agents) and the blackboard with subscription (agents subscribe to topics, CA-MCP/Matrix, scales further but needs schema design). The reference failure mode is memory poisoning: one agent hallucinates a "fact," downstream agents treat it as verified, and accuracy decays gradually — harder to debug than a crash. Builds both, injects a poisoning attack, shows the three proven mitigations (provenance, unwritable verifier, schema constraints).
    **Tools/Frameworks:** Python stdlib + `threading`, message pool, blackboard/subscription, CA-MCP, Matrix framework, MAST memory-poisoning taxonomy.

14. ### 14 · Consensus and Byzantine Fault Tolerance for Agents — **Learn + Build** · Python · ~75min
    Classical PBFT (Castro & Liskov 1999, tolerates `f < n/3` Byzantine nodes) meets stochastic LLMs that violate all three PBFT assumptions (independent faults, truly-honest honest nodes, ground-truth answers). Three 2025–2026 adaptations — CP-WBFT (confidence-probed weighted voting, +85.71% BFT on complete graphs), DecentLLMs (leaderless parallel proposals + geometric-median aggregation, robust past `f < n/2`), WBFT (weighted voting + hierarchical clustering). Injects three LLM-specific attacks (byzantine lie, sycophantic conformity, correlated-error monoculture) and measures each variant.
    **Tools/Frameworks:** PBFT, CP-WBFT, DecentLLMs (geometric median), WBFT, confidence probes, Mixture-of-Agents.

15. ### 15 · Voting, Self-Consistency, and Debate Topology — **Learn + Build** · Python · ~75min
    Self-consistency (Wang 2022, sample one model N times and majority-vote) extended with heterogeneous agents (different models/prompts/temperatures) to escape monoculture; beyond majority vote, topology matters. MultiAgentBench (ACL 2025) found graph best for research with a coordination tax past ~4 agents; AgentVerse documents volunteer and conformity behaviors, conformity being both a feature (consensus) and a risk (groupthink). Maps the four topologies (star/chain/tree/graph), builds each, measures the coordination tax.
    **Tools/Frameworks:** self-consistency (Wang 2022), A-HMAD, MultiAgentBench/MARBLE, AgentVerse, star/chain/tree/graph topologies.

16. ### 16 · Negotiation and Bargaining — **Learn + Build** · Python · ~75min
    Agents negotiating resources/prices/tasks: LLMs alone close tightly-parameterized deals at ~27% (scale doesn't help — bigger models make better language, not better strategy). The winning decomposition is OG-Narrator (deterministic offer generator computes numeric moves, LLM only narrates → deal rate 26.67%→88.88%); chain-of-thought-concealing agents win by hiding reasoning. Implements Contract Net Protocol (the FIPA ancestor from Lesson 02), wires an LLM buyer/seller, runs an OG-Narrator decomposition, measures deal-rate deltas.
    **Tools/Frameworks:** Contract Net Protocol (Smith 1980/FIPA), OG-Narrator, NegotiationArena, Rubinstein/Zeuthen/tit-for-tat strategies.

17. ### 17 · Generative Agents and Emergent Simulation — **Learn + Build** · Python · ~75min
    Park et al. 2023's Smallville sandbox (25 agents) with a three-part architecture — memory stream (recency/importance/relevance-scored log), reflection (higher-order syntheses fed back into the stream), plan (day→hour→action decomposition) — producing the landmark Valentine's Day party emergence from unscripted agents. Ablations show all three components are required for believability; documented failures are spatial-norm errors. This is the reference architecture for 2026 agent simulations and social evaluation.
    **Tools/Frameworks:** Park 2023 Smallville architecture, memory stream, reflection, plan decomposition, recency/importance/relevance scoring.

18. ### 18 · Theory of Mind and Emergent Coordination — **Learn + Build** · Python · ~75min
    Li et al. 2023 showed LLM agents exhibit emergent higher-order Theory of Mind (reasoning about beliefs about beliefs) but fail on long-horizon planning; Riedl 2025 measured that only the ToM-prompt condition produces identity-linked differentiation and goal-directed complementarity — coordination emergence is prompt-conditional and model-dependent, not free. Builds a minimal ToM-aware agent, runs a cooperative task with and without ToM prompting, measures the coordination delta against the Riedl protocol (Sally-Anne false-belief test framing).
    **Tools/Frameworks:** Li 2023 ToM game, Riedl 2025 synergy measurement, Sally-Anne test, zeroth/first/second-order ToM prompting.

19. ### 19 · Swarm Optimization for LLMs (PSO, ACO) — **Learn + Build** · Python · ~75min
    Bio-inspired optimization's LLM comeback: LMPSO (particle velocity is a prompt, LLM generates the next candidate) for structured-sequence outputs; Model Swarms (each LLM expert a PSO particle on a model-weight manifold, +13.3% average over 12 baselines on 9 datasets); AMRO-S (ACO-inspired pheromone specialists for agent routing, 4.7× speedup). Implements PSO on prompt-parameter space and ACO on agent routing; the fit is gradient-free, population-based, cheap-per-evaluation — exactly the prompt/routing regime backprop can't touch.
    **Tools/Frameworks:** PSO (Kennedy & Eberhart 1995), ACO, LMPSO, Model Swarms, SwarmPrompt, AMRO-S, pheromone routing.

20. ### 20 · MARL — MADDPG, QMIX, MAPPO — **Learn** · Python · ~90min
    The RL heritage that informs LLM-agent coordination, via Centralized Training Decentralized Execution: MADDPG (each critic sees all states/actions in training, local actors at test — cooperative/competitive/mixed), QMIX (monotonic value decomposition so `argmax` distributes cleanly, dominant on StarCraft SMAC), MAPPO (PPO with a centralized value function, "surprisingly effective" with minimal tuning — the 2026 default cooperative-MARL baseline). Builds each from a small grid-world toy so CTDE, value decomposition, and centralized critics land as pattern vocabulary before LLM-agent training.
    **Tools/Frameworks:** MADDPG (Lowe 2017), QMIX (Rashid 2018), MAPPO (Yu 2022), CTDE, Particle World/SMAC/Google Football/Hanabi.

21. ### 21 · Agent Economies, Token Incentives, Reputation — **Learn** · Python · ~75min
    Long-horizon autonomous agents need economic agency: the emerging five-layer stack (DePIN compute → W3C DID identity/reputation → cognition RAG+MCP → account-abstraction settlement → agentic-DAO governance). Production networks Bittensor (TAO subnets reward task-specific quality), Fetch.ai/ASI (ASI-1 Mini + FET), Gonka (transformer proof-of-work reallocating compute to productive tasks); academic Shapley-value credit attribution and second-price token auctions under monotone aggregation. Builds a minimal agent marketplace, applies Shapley attribution, runs a second-price auction.
    **Tools/Frameworks:** Bittensor/TAO, Fetch.ai/ASI-1/FET, Gonka, W3C DIDs, ERC-4337 account abstraction, ANP, Shapley-value attribution, token auctions.

22. ### 22 · Production Scaling — Queues, Checkpoints, Durability — **Learn + Build** · Python · ~75min
    Scaling to thousands of concurrent runs requires durable execution: LangGraph writes a checkpoint after each super-step keyed by `thread_id` (Postgres default), worker crashes release leases and another worker resumes, agents sleep indefinitely waiting for human input. MegaAgent ran per-agent producer-consumer queues (Idle/Processing/Response); async/fiber beats thread-per-job for LLM streaming (threads idle 99% waiting for tokens). Counterpoint — Bedi's "FastAPI + Postgres + nothing else until load proves otherwise" — lands the pragmatic start-simple rule.
    **Tools/Frameworks:** LangGraph runtime, Temporal, Postgres+SQS/RabbitMQ, MegaAgent producer-consumer, `asyncio`/`sqlite3`, FastAPI.

23. ### 23 · Failure Modes — MAST, Groupthink, Monoculture, Cascading Errors — **Learn** · Python · ~75min `[GAP 2: complexity ladder]`
    The MAST reference taxonomy (Cemri et al., NeurIPS 2025, 1642 traces, 41–86.7% failure rate): Specification Problems 41.77% (role ambiguity, underspecified tasks), Coordination Failures 36.94% (state desync, lost messages), Verification Gaps 21.30% (no independent check). The Groupthink family (monoculture collapse, conformity bias, deficient ToM, mixed-motive dynamics, cascading reliability failures like retry storms) plus memory poisoning. STRATUS reports 1.5× mitigation improvement via specialized detection/diagnosis/validation agents — failure modes treated as first-class design inputs that decide when multi-agent is the wrong choice.
    **Tools/Frameworks:** MAST (Cemri 2025), Groupthink taxonomy, STRATUS, monoculture/conformity/cascading detectors, retry-storm circuit breakers.

24. ### 24 · Evaluation and Coordination Benchmarks — **Learn** · Python · ~75min
    Five 2025–2026 benchmarks: MARBLE/MultiAgentBench (ACL 2025, star/chain/tree/graph, graph best for research, coordination tax past ~4 agents); COMMA (multimodal asymmetric-info, frontier models struggle to beat random); MedAgentBoard (multi-agent does NOT dominate single-LLM on most categories); AgentArch (enterprise architectures); SWE-bench Pro (1865 problems, ~23% frontier vs 70%+ Verified — the contamination reality check). Pins the rule "just passing SWE-bench Verified is not evidence of generalization" and the AAAI 2026 WMAC bridge program as the community focal point.
    **Tools/Frameworks:** MARBLE/MultiAgentBench, COMMA, MedAgentBoard, AgentArch, SWE-bench Pro, Verdent scaffold, AAAI 2026 WMAC.

25. ### 25 · Case Studies and the 2026 State of the Art — **Learn (capstone)** · — · ~90min
    Three production references read end-to-end: Anthropic's Research system (orchestrator-worker, 15× tokens, +90.2% over single-agent Opus 4, rainbow deployments, scale-effort-to-complexity) as the canonical supervisor case; MetaGPT/ChatDev (SOP role specialization, communicative dehallucination, MacNet to >1000 agents via DAGs) as the role-decomposition case; and OpenClaw/Moltbook (population-scale emergent economy, prompt-injection risk, state-level regulation) as the swarm-scale case. Maps the April 2026 framework landscape (LangGraph/CrewAI lead production; AG2 is the AutoGen continuation; Microsoft AutoGen merged into Microsoft Agent Framework; OpenAI Agents SDK and Google ADK) with the common patterns distilled.
    **Tools/Frameworks:** Anthropic Research system, MetaGPT/ChatDev/MacNet, OpenClaw/Moltbook, LangGraph, CrewAI, AG2, Microsoft Agent Framework, OpenAI Agents SDK, Google ADK, MCP/A2A support.

---

## Notes for the lesson-level audit

- **The complexity-ladder material (Gap 2) lands in a deliberate spine across all three phases.** Phase 14 owns the workflow-vs-agent distinction (Lesson 12, Anthropic's five patterns) and the "add multi-step agentic systems only when needed" eval rule (Lesson 30), plus the "start simple, add topology only when insufficient" orchestration framing (Lesson 28). Phase 15 adds the autonomy-level decision (Lessons 1, 7, 8 — long-horizon breakage, the capability-vs-alignment race, bounded-self-improvement primitives). Phase 16 bookends it: Lesson 01 (Why Multi-Agent) opens with the single-agent ceiling and when splitting is the right move; Lesson 23 (MAST failure modes) closes with the 41–86.7% failure-rate evidence for when multi-agent is the wrong move. The audit may want to surface these as a tagged thread the way the eval thread was handled in Module 1.
- **The single-agent → autonomous → multi-agent arc is real and sequential.** Phase 14 builds one reliable agent (loop → memory → tools → frameworks → workbench capstone); Phase 15 takes that agent long-horizon and bolts on the safety/governance stack (permission modes, durable execution, cost governors, kill switches, HITL propose-then-commit, constitutional/guardrail/RSP/FSF/METR layers); Phase 16 multiplies the agent and studies coordination (primitives → topologies → protocols → consensus/negotiation → economies → production scaling). Phase 16 Lesson 04's four-primitive model (Agent/Handoff/Shared-state/Orchestrator) is the single diagram that makes the whole module legible.
- **"Start simple" is the most-repeated engineering rule across all three phases** — Anthropic's workflow patterns (14.12), the orchestration "build the right system" gate (14.28), eval-driven "add agentic systems only when needed" (14.30), CrewAI "start with a Flow" (14.15), Bedi's "FastAPI + Postgres + nothing else" (16.22), and the MAST evidence that 41.77% of failures are specification problems before you even reach coordination (16.23). Worth noting to the audit as the module's through-line.
- **Two seam lessons bridge modules.** Phase 16 Lessons 19 (PSO/ACO) and 20 (MARL) reach back into Phase 09 (Reinforcement Learning) and classical optimization — they're the formal-methods underpinning of the informal "swarm" patterns in 16.09/16.22, included because 2026 LLM-agent papers (LMPSO, Model Swarms, AMRO-S, MAPPO baselines) cite them directly. The audit may want to flag the Phase 09 dependency.
- **Capstone cluster at the tail of Phase 14 (Lessons 31–42).** The 12-lesson workbench mini-track (why models fail → minimal workbench → rules/state/init/scope/feedback/verification/reviewer/handoff → real-repo comparison → shippable pack) is self-contained and produces a concrete artifact (`agent-workbench-pack/`). It is the most production-ready material in the module and the natural handoff into Phase 15's autonomous-systems concerns; the audit should treat 31–42 as a unit rather than 12 discrete lessons.
