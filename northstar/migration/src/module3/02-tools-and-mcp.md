# Tools & MCP

> **Migrated from** `aefs-module3-tools-protocols` (Ph13, 23 lessons — **the canonical MCP spine**) +
> `aefs-module3-agent-engineering` (Ph14 06 tool use) + `asdg` Ch17/Ch07.03 (lighter, folded in). **The big
> merge:** MCP was covered 4×; this is the one spine.

## Tool use

The tool interface — describe → decide → execute → observe. JSON-Schema tool contracts, argument validation
and coercion, execution sandboxing. BFCL V4 finding: single-turn calling is near-solved; failures
concentrate in memory, dynamic decisions, long-horizon chains, and hallucination detection.

## The MCP spine (aefs Ph13, canonical)

The Model Context Protocol — the JSON-RPC 2.0 standard for how hosts connect to tools, data, and agents:

```
fundamentals → server → client → transports (stdio / streamable HTTP)
→ resources & prompts → sampling → roots & elicitation → async tasks → apps
→ security (tool poisoning) → OAuth 2.1 → gateways & registries → A2A handoff
```

Build a runnable server/client pair exposing tools, resources, and prompts; implement capability scoping,
mutation allowlists, and tool-poisoning defenses.

**TypeScript enters here** — typed tool definitions (`Tool<TInput, TOutput>`) and MCP server contracts are
the first place product-layer code gets written (see the TypeScript chapter).

**Forward-pointer:** OpenTelemetry GenAI semantic conventions (Ph14 23) standardize agent telemetry — the
deep observability stack is Module 5.
