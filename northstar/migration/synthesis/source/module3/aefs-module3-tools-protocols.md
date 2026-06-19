# Module 3 · Tools & Protocols — Phase 13 Extract

> Source: `phases/13-tools-and-protocols/` (23 lessons, 01–23). Phase README is a stub; all content lives in per-lesson `docs/en.md`.
> This is the **tool-interface and MCP module**: the tool/function-calling interface, schema design, the Model Context Protocol (fundamentals, server, client, transports, resources/prompts, sampling, roots/elicitation, async tasks, apps), MCP security (tool poisoning, OAuth 2.1, production auth), gateways/registries, A2A, OpenTelemetry for GenAI, routing, skills/agent-SDKs, and a capstone tool ecosystem.
> Tag legend: `[THREAD: safety]` = security / governance / auth control surface.

## Lessons

### 01 · The Tool Interface — Why Agents Need Structured I/O — **Learn** · Python (stdlib, no LLM) · ~45 minutes
This lesson establishes the four-step tool-call loop (describe → decide → execute → observe) as the fundamental invariant underlying all modern LLM tool-calling mechanisms, including OpenAI/Anthropic/Gemini function calling, MCP's `tools/call`, and A2A task delegation. Students build a working simulation of the full loop harness—including a tool registry, a minimal JSON Schema validator, and an iteration circuit breaker—using a fake pattern-matching decider to simulate the LLM without requiring API calls, producing a skill artifact that audits draft tool definitions for loop fitness. **Protocols/Tools:** function-calling, JSON Schema, MCP, A2A.

### 02 · Function Calling Deep Dive — **Build** · Python (stdlib, schema translators) · ~75 minutes
This lesson performs a side-by-side diff of the function-calling payload shapes for OpenAI, Anthropic, and Gemini, teaching how to translate a single canonical tool declaration across all three formats while navigating provider-specific limits and strict-mode constraints. The student builds a local schema translator harness that unifies declarations and parses representative response shapes into a single call object without making network requests.
**Protocols/Tools:** function-calling, JSON Schema, OpenAPI 3.0 subset.

### 03 · Parallel Tool Calls and Streaming with Tools — **Build** · Python (stdlib, thread pool + streaming harness) · ~75 minutes
This lesson teaches the mechanics of executing multiple tool calls concurrently within a single LLM turn, contrasting sequential and parallel fan-out latency. Students build a Python harness using `concurrent.futures.ThreadPoolExecutor` that benchmarks sequential versus parallel execution of simulated weather API calls, alongside a `StreamAccumulator` that correctly reassembles interleaved, streamed partial JSON arguments keyed by `tool_call_id`.
**Protocols/Tools:** function-calling, JSON Schema, OpenAI API, Anthropic API, Gemini API, `streamFunctionCallArguments`, `asyncio.gather`

### 04 · Structured Output — JSON Schema, Pydantic, Zod, Constrained Decoding — **Build** · Python (stdlib, JSON Schema 2020-12 subset) · ~75 minutes

This lesson teaches constrained decoding and schema enforcement for LLM outputs, contrasting three approaches (prompt-only, validate-after-generation, and decode-time enforcement) and explaining why strict mode collapses failure modes from six categories down to a single typed refusal. Students build a minimal JSON Schema 2020-12 validator in Python stdlib that handles types, required fields, enums, min/max, patterns, items, and `additionalProperties: false`, then run fake LLM outputs through it to demonstrate parse error, schema violation, and refusal code paths. The artifact ships an `Invoice` extraction schema with typed `ValidationError` lists surfaced for retry prompts and a refusal branch that logs and returns without retrying.

**Protocols/Tools:** JSON Schema 2020-12, OpenAI strict mode, constrained decoding, Pydantic v2, Zod, grammar-based decoding (outlines, guidance, lm-format-enforcer), logit masking, speculative decoding, JSON-RPC function-calling patterns.

### 05 · Tool Schema Design — Naming, Descriptions, Parameter Constraints — **Learn** · Python (stdlib, tool schema linter) · ~45 minutes [THREAD: safety]

This lesson teaches the naming conventions, description patterns, and parameter constraint rules that drive tool-selection accuracy in LLM function-calling and MCP registries, citing measured 10–20 percentage-point swings on benchmarks like StableToolBench. Students build a tool-schema linter (`code/main.py`) that audits a tool registry against design rules — flagging naming violations, missing "Do not use for" disambiguation sentences, monolithic `action: str` designs, untyped fields, and indirect-injection keywords in descriptions — and produces a fix-list skill artifact (`outputs/skill-tool-schema-linter.md`) suitable for CI integration.

**Protocols/Tools:** function-calling, JSON Schema, MCP, StableToolBench, MCPToolBench++, SafeToolBench

### 06 · MCP Fundamentals — **Learn** · Python (stdlib, JSON-RPC parser) · ~45 minutes
This lesson introduces the Model Context Protocol (MCP) specification (2025-11-25), an open standard for model-to-tool discovery and invocation. Students learn the six primitives (tools, resources, prompts, roots, sampling, elicitation), the three-phase lifecycle (initialize, operation, shutdown), and capability negotiation via JSON-RPC 2.0 wire formats. The artifact is a minimal JSON-RPC 2.0 parser/emitter that walks through the `initialize` → `tools/list` → `tools/call` → `shutdown` sequence by hand, printing every message shape.
**Protocols/Tools:** MCP (spec 2025-11-25), JSON-RPC 2.0, stdio, Streamable HTTP

### 07 · Building an MCP Server — Python + TypeScript SDKs — **Build** · Python (stdlib, stdio MCP server) · ~75 minutes
This lesson teaches end-to-end implementation of a notes-focused MCP server using newline-delimited stdio transport and manual JSON-RPC dispatching. Students implement capability negotiation, all three server primitives (tools, resources, prompts), and structured error handling to graduate from a stdlib script to a high-level SDK. The concrete artifact is a functional MCP server and a scaffolder skill markdown file.
**Protocols/Tools:** MCP, JSON-RPC 2.0, stdio, FastMCP, Python SDK, TypeScript SDK.

### 08 · Building an MCP Client — Discovery, Invocation, Session Management — **Build** · Python (stdlib, multi-server MCP client) · ~75 minutes
This lesson teaches the orchestration logic required to host multiple MCP servers simultaneously, covering child-process spawning, capability negotiation, per-server session state management, and tool-list merging. The student builds a complete multi-server MCP client that lifts three simulated MCP servers into a single flat tool namespace with explicit namespace-collision resolution and dispatch routing.
**Protocols/Tools:** MCP, JSON-RPC 2.0, stdio, function-calling, JSON Schema

### 09 · MCP Transports — stdio vs Streamable HTTP vs SSE Migration — **Learn** · Python (stdlib, Streamable HTTP endpoint skeleton) · ~45 minutes

This lesson teaches the architectural and operational differences between MCP's stdio (local child-process) and Streamable HTTP (remote single-endpoint) transports, covering session-id lifecycle, `Origin` validation for DNS-rebinding defense, and SSE stream reconnection via `last-event-id`. Students build a minimal Streamable HTTP `/mcp` endpoint using Python's `http.server` that handles POST, GET, and DELETE methods, enforces `Mcp-Session-Id` headers, and rejects non-allowlisted origins, ultimately producing a migration skill document for legacy HTTP+SSE servers.

**Protocols/Tools:** MCP, JSON-RPC 2.0, stdio, Streamable HTTP, HTTP+SSE (legacy), SSE, `Mcp-Session-Id`, `Origin` validation, `last-event-id`, Cloudflare Workers, Vercel Functions, gRPC.

### 10 · MCP Resources and Prompts — Context Exposure Beyond Tools — **Build** · Python (stdlib, resource + prompt handler) · ~45 minutes
This lesson teaches the MCP decision rule for splitting server capabilities across tools (computed actions), resources (data for context attachment), and prompts (reusable slash-command workflows), walking through the full `resources/*` and `prompts/*` JSON-RPC message flows including list, read, subscribe, and update notifications. The student extends a notes MCP server with URI-addressable note resources, a dynamic recent-notes resource, file-watcher-driven subscription updates, and a multi-message `review_note` prompt template, producing a `skill-primitive-splitter.md` artifact that classifies proposed server capabilities by primitive type.
**Protocols/Tools:** MCP, JSON-RPC 2.0, resources/list, resources/read, resources/subscribe, notifications/resources/updated, notifications/resources/list_changed, prompts/list, prompts/get, resource templates, URI schemes (file://, notes://, postgres://, memory://, ui://).

### 11 · MCP Sampling — Server-Requested LLM Completions and Agent Loops — **Build** · Python (stdlib, sampling harness) · ~75 minutes [THREAD: safety]

This lesson teaches MCP sampling (`sampling/createMessage`), the mechanism by which a server can request LLM completions from the client without holding any model credentials or API keys. Students build a server-to-client sampling harness in Python that implements a `summarize_repo` tool running a two-round agent loop (file selection then summarization), complete with model preferences, rate limiting, and the SEP-1577 experimental tool-in-sampling extension. The lesson covers human-in-the-loop confirmation requirements, loop bomb prevention, and safety risks including covert sampling and resource theft.

**Protocols/Tools:** MCP, JSON-RPC 2.0, `sampling/createMessage`, modelPreferences, SEP-1577, function-calling, JSON Schema

### 12 · Roots and Elicitation — Scoping and Mid-Flight User Input — **Build** · Python · ~45 minutes

This lesson teaches two MCP client primitives that address common production failure modes: roots, which scope server file operations to a client-declared set of URIs, and elicitation, which lets a server pause mid-tool-call to request structured user input via a form or browser URL. The student extends a notes MCP server with boundary enforcement (rejecting out-of-root writes), `roots/list` re-querying on `notifications/roots/list_changed`, and two elicitation patterns — form-mode disambiguation in `notes_delete` and experimental URL-mode (SEP-1036) first-run setup in `notes_setup`. The concrete artifact is `code/main.py` running three scenarios (happy path, disambiguation, out-of-root rejection) plus a skill file (`outputs/skill-elicitation-form-designer.md`) that designs elicitation schemas and message templates for tools needing user confirmation.

**Protocols/Tools:** MCP, JSON-RPC 2.0, roots, elicitation, `elicitation/create`, `roots/list`, `notifications/roots/list_changed`, JSON Schema, SEP-1036, OAuth (URL-mode)

### 13 · Async Tasks (SEP-1686) — Call-Now, Fetch-Later for Long-Running Work — **Build** · Python (stdlib, async task state machine) · ~75 minutes

This lesson teaches SEP-1686 task augmentation for MCP, where synchronous tool calls exceeding 30 seconds are promoted to background tasks with durable state persistence. Students build a filesystem-backed task store with a background worker thread implementing the full task lifecycle (`working` → `completed`/`failed`/`cancelled`), polling via `tasks/status`, result fetching via `tasks/result`, cooperative cancellation, and crash recovery that marks orphaned tasks as `CRASH_RECOVERY`. The artifact is a runnable async task system plus a design skill document (`outputs/skill-task-store-designer.md`) for sizing TTL, durability layers, and `taskSupport` flags on long-running tools.

**Protocols/Tools:** MCP, JSON-RPC 2.0, SEP-1686, tasks/status, tasks/result, tasks/cancel, tasks/list, notifications/tasks/updated, JSON Schema, stdio, sampling/createMessage, SQLite, Redis.

### 14 · MCP Apps — **Build** · Python, HTML · ~75 minutes
This lesson teaches the MCP Apps extension (SEP-1724) for returning sandboxed, interactive HTML from tool calls via the `ui://` resource scheme and `text/html;profile=mcp-app` MIME type. Students build a `visualize_timeline` tool in a Python MCP server that emits a complete HTML bundle with an SVG timeline, configures Content-Security-Policy (CSP) via `_meta.ui`, and documents the `postMessage` JSON-RPC 2.0 dialect for UI-to-host communication. [THREAD: safety]

**Protocols/Tools:** MCP, SEP-1724 (MCP Apps), JSON-RPC 2.0, `ui://` resource scheme, `text/html;profile=mcp-app` MIME, iframe sandbox, `postMessage`, Content-Security-Policy (CSP), Permissions-Policy, `ui/initialize` handshake, AppRenderer, AppFrame, function-calling.

### 15 · MCP Security I — Tool Poisoning, Rug Pulls, Cross-Server Shadowing — **Learn** · Python (stdlib, hash-pin + poisoning detector) · ~45 minutes [THREAD: safety]
This lesson catalogs seven concrete MCP attack classes—tool poisoning, rug pulls, cross-server shadowing, MPMA, parasitic toolchains, sampling attacks, and supply-chain masquerading—and explains why each succeeds despite the tool interface appearing legitimate. Students build a CI-runnable tool-poisoning detector in Python (`code/main.py`) that combines regex-based static analysis of description text with a hash-pinning store that flags post-approval description mutations.
**Protocols/Tools:** MCP, JSON Schema, `mcp-scan`, MELON (masked re-execution), Rule of Two.

### 16 · MCP Security II — OAuth 2.1, Resource Indicators, Incremental Scopes — **Build** · Python (stdlib, OAuth state machine simulator) · ~75 minutes [THREAD: safety]

This lesson implements the MCP 2025-11-25 OAuth 2.1 profile — authorization code + PKCE, resource indicators (RFC 8707), protected-resource metadata (RFC 9728), and SEP-835 incremental scope consent — as an in-memory state machine that traces every hop of the step-up authorization flow. The concrete artifact is a Python simulator (`code/main.py`) covering PKCE generation, token audience validation, and `insufficient_scope` handling, plus a skill document (`outputs/skill-oauth-scope-planner.md`) for designing scope sets and step-up policies for remote MCP servers.

**Protocols/Tools:** MCP (2025-11-25 spec), OAuth 2.1, PKCE, RFC 8707 (resource indicators), RFC 9728 (protected-resource metadata), SEP-835 (incremental scope consent / step-up authorization), Bearer token authentication, `WWW-Authenticate`, `.well-known/oauth-protected-resource`, stdio.

### 17 · MCP Gateways and Registries — Enterprise Control Planes — **Learn** · Python (stdlib, minimal gateway) · ~45 minutes [THREAD: safety]
This lesson explains where an MCP gateway sits between clients and multiple backend MCP servers and teaches the five core gateway responsibilities: auth, RBAC, audit logging, rate limiting, and policy enforcement. Students build a minimal stdlib gateway (~150 lines) in `code/main.py` that authenticates users via Bearer tokens, enforces per-user RBAC and token-bucket rate limits, routes requests to two backend servers, appends every call to an audit log, and rejects any backend tool whose description hash does not match a pinned SHA256 manifest. The lesson also surveys the 2026 vendor landscape (Cloudflare, Kong, IBM, Envoy, etc.) and contrasts the Official MCP Registry (`registry.modelcontextprotocol.io`, reverse-DNS namespace-verified) against metaregistries like Glama, MCPMarket, MCP.so, Smithery, and LobeHub.
**Protocols/Tools:** MCP, OAuth 2.1, JSON Schema, OpenTelemetry, Streamable HTTP, OPA/Rego, Kyverno, Styra, tool-hash pinning, RBAC, token-bucket rate limiting, reverse-DNS naming.

### 18 · MCP Auth in Production — Enrollment, JWKS Refresh, Audience-Pinned Tokens — **Build** · Python (stdlib) · ~90 minutes [THREAD: safety]

This lesson models the complete production OAuth 2.1 authorization surface for MCP servers by separating operations into three distinct roles: an authorization server, a resource server, and a client. Students implement scalable client enrollment (via Client ID Metadata Documents or RFC 7591 fallback), RFC 8414 metadata discovery, scheduled JWKS cache refresh to survive key rotation, and RFC 8707 audience-pinned token validation to refuse cross-resource replay attacks. The concrete artifact built is a standard-library Python simulation (`code/main.py`) that executes a full flow from discovery to a validated tool call, alongside an output skill document (`outputs/skill-mcp-auth.md`) detailing deployment surfaces and refusal rules.

**Protocols/Tools:** MCP, OAuth 2.1, RFC 8414, RFC 9728, Client ID Metadata Documents (CIMD), RFC 7591 (Dynamic Client Registration), RFC 8707, RFC 7636 (PKCE), RFC 9207, JWKS, JWT, OAuth 2.0 Bearer Token, WWW-Authenticate.

### 19 · A2A — Agent-to-Agent Protocol — **Build** · Python (stdlib, Agent Card + Task harness) · ~75 minutes

This lesson teaches the Agent-to-Agent (A2A) protocol — an open standard for cross-framework agent collaboration where opaque agents delegate Tasks to one another with lifecycle management. Students build a minimal A2A harness using Python stdlib and an in-memory transport, implementing the Agent Card publication at `/.well-known/agent.json`, the full Task lifecycle (submitted → working → input-required → completed), Messages with mixed-type Parts (text, file, data), and Artifact return. The produced artifact is `outputs/skill-a2a-agent-spec.md`, which defines the Agent Card JSON, skills schema, and endpoint blueprint for a new callable agent.

**Protocols/Tools:** A2A, JSON-RPC over HTTP, gRPC, SSE, AP2 (Agent Payments Protocol), JWT-signed Agent Cards, HMAC, `/.well-known/agent.json`, MCP (comparison only).

### 20 · OpenTelemetry GenAI — Tracing Tool Calls End-to-End — **Build** · Python (stdlib, OTel span emitter) · ~75 minutes
This lesson teaches the OpenTelemetry GenAI semantic conventions (stable v1.37+) for tracing an agent loop, LLM calls, tool execution, and MCP client dispatch under a single trace id. Students build a stdlib OTel span emitter that outputs OTLP-JSON-shaped spans with required `gen_ai.*` attributes, and also produce an instrumentation plan (`skill-otel-genai-instrumentation.md`) for adding spans to an existing codebase.
**Protocols/Tools:** OpenTelemetry, GenAI semantic conventions, OTLP, W3C traceparent, JSON-RPC, stdio, Streamable HTTP, Jaeger, Langfuse, Arize Phoenix, OpenLLMetry, AgentOps, Datadog, Honeycomb.

### 21 · LLM Routing Layer — LiteLLM, OpenRouter, Portkey — **Learn** · Python (stdlib, routing + failover + cost tracker) · ~45 minutes [THREAD: safety]

This lesson covers provider routing through gateway architectures, teaching the distinctions between self-hosted (LiteLLM), managed SaaS (OpenRouter), and production-grade (Portkey) options using an OpenAI-compatible proxy shape. Students build a ~150-line routing gateway that accepts OpenAI-shaped requests, translates them to per-provider stubs, executes a priority fallback chain on 5xx errors, tracks per-request cost via token-usage multiplication, and applies PII redaction on inputs. The lesson also covers model aliases, semantic caching, guardrails, per-key rate limits, routing strategies (static, load-balanced, cost-aware, latency-aware, task-aware), and how MCP sampling requests can be routed through the same gateway.

**Protocols/Tools:** OpenAI-compatible API, MCP, function-calling, OpenTelemetry, JSON Schema, PII redaction, semantic caching, SHA256

### 22 · Skills and Agent SDKs — **Learn** · Python (stdlib, SKILL.md parser and loader) · ~45 minutes

This lesson distinguishes the three layers of the 2026 agent stack — AGENTS.md for project-level context loaded at session start, SKILL.md for portable reusable workflow know-how invoked on demand, and MCP for callable tools — and teaches how a single bundle composes across Claude Code, Cursor, and Codex. The student builds a stdlib SKILL.md parser and loader in Python that discovers skills under `./skills/`, parses YAML frontmatter and markdown bodies, simulates an agent loop invoking a skill by name, and demonstrates progressive disclosure via an on-demand sub-resource reader, producing a combined SKILL.md + AGENTS.md + MCP-server-blueprint bundle as the shipped artifact.

**Protocols/Tools:** MCP, SKILL.md, AGENTS.md, Anthropic Claude Agent SDK, OpenAI Apps SDK, SkillKit, YAML frontmatter, progressive disclosure, filesystem skill discovery.

### 23 · Capstone — Build a Complete Tool Ecosystem — **Build** · Python (stdlib, end-to-end ecosystem harness) · ~120 minutes [THREAD: safety]

This capstone integrates every primitive from Phase 13 into a single production-shaped system implementing a "research and report" workflow: searching arXiv via MCP tools, delegating summarization to an A2A sub-agent, rendering an interactive report as a `ui://` resource, and tracing all hops with OpenTelemetry GenAI spans. Students build a complete ecosystem harness in `code/main.py` that demonstrates a gateway-fronted multi-server MCP client with OAuth 2.1 + PKCE, RBAC enforcement, pinned tool-description hashes, and packaging via `AGENTS.md` + `SKILL.md`.

**Protocols/Tools:** MCP, A2A, OAuth 2.1, PKCE, RBAC, OpenTelemetry, GenAI semconv, JSON Schema, stdio, tool-poisoning detection, AGENTS.md, SKILL.md, Rule of Two audit
