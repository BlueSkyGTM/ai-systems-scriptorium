# Structured Output and Tools

A model that returns free-form prose is useful. A model whose output you can parse, validate, and act on without writing defensive exception handlers is a system component. That shift, from useful to reliable, is what structured output and tools accomplish.

You build the layer that makes a model's output trustworthy enough to drive application logic.

## Structured Outputs

The model doesn't return JSON because you asked nicely. It returns JSON because you constrained the decoding. The spectrum runs from weakest to strongest enforcement:

1. **Prompt-based instruction**; "return a JSON object with keys `name` and `score`." Fails on edge cases. Fine for prototypes.
2. **Schema-validated response**; define a JSON Schema, parse the response, reject on validation error with a retry loop that feeds the validation error back to the model. Reliable for simple schemas.
3. **Constrained decoding**; the model's token logits are masked at inference time to make invalid tokens impossible. The output is structurally valid by construction, not by retry. Tools like Outlines and XGrammar implement this; provider APIs (Anthropic tool use, OpenAI Structured Outputs) implement it at the server.

In production, provider-level constrained decoding is the right default; no retry overhead, no parsing guards, no edge-case debugging. Use schema validation with retries when you're working against a model or deployment that doesn't support constrained decoding.

Define your schema in Pydantic. Derive the JSON Schema from the Pydantic model programmatically; don't maintain two representations of the same structure.

## Function Calling and Tool Use

Function calling is the five-step loop that converts a schema definition into an executable action:

1. Define your tool as a JSON Schema contract; name, description, parameter types, required fields.
2. Pass the tool definition in the API request alongside the user message.
3. The model emits a `tool_use` block naming the tool and the arguments it wants to call with.
4. You validate the arguments against the schema, execute the function, and capture the result.
5. Feed the result back to the model in the next turn. The model generates its final response grounded in the tool output.

The model doesn't call anything. You do; the model emits intent; you execute. This separation is not incidental; it's the security boundary. You control what functions exist, what arguments they accept, and what they're allowed to touch. Never trust the model's arguments without validating them against your schema before execution.

Parallel tool calls let the model request multiple tools in a single turn. Execute them concurrently where the results are independent. Sequential execution of parallelizable tool calls is a common performance mistake.

Build a tool registry rather than scattered function definitions. The registry holds the schema definitions, the callable implementations, and the authorization rules. A tool call from the model hits the registry, which validates the caller's permissions before dispatching.

## MCP; the On-Ramp

The Model Context Protocol (MCP) is a JSON-RPC 2.0 wire format that standardizes how a host (your application) connects to tool servers. Instead of baking tool implementations directly into your application, you run an MCP server, a small process that exposes tools over stdio or HTTP, and the host discovers and calls them through a standard protocol.

The value is decoupling. An MCP server for your internal database can be used by Claude Code, Claude Desktop, or your own application without rebuilding the tool integration each time. The tool implementation lives in one place; the protocol handles the rest.

Build MCP awareness here. The full protocol depth, transports, OAuth, gateways, multi-server registries, is Module 3.

Defend against tool poisoning. A malicious tool description can instruct the model to leak context or call unauthorized functions. Validate tool descriptions before registering them; treat tool sources you don't control as untrusted.

## Feeding Module 3

Reliable tool calls are the prerequisite for agents. An agent is a loop: model decides → tool executes → result feeds back → model decides again. Every turn of that loop depends on structured output (the model's decision must be parseable) and tool execution (the action must actually run). The agent patterns in Module 3 build on the two primitives you're assembling here.

Structured output plus tools is the boundary between a chatbot and a system that does things.

## Core Concepts

- Provider-level constrained decoding makes structurally valid output impossible to violate; prefer it over prompt-based JSON instructions and retry loops.
- The function-calling loop has five steps; the model emits intent, you execute; the security boundary is your responsibility, not the model's.
- A tool registry centralizes schema definitions, implementations, and authorization rules so a tool call can be validated before it runs.
- MCP standardizes host-to-tool connections over JSON-RPC 2.0 so a tool implementation can serve multiple hosts without rebuilding the integration.

<div class="claude-handoff" data-exercise="exercises/module2/06-structured-output-and-tools/">

**Build It in Claude Code**: Build a tool registry with three tools (a calculator, a search stub, and a file reader), wire it to a model call using function calling, validate tool arguments before execution, and handle parallel tool calls in a single turn.

</div>
