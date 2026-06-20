# Exercise: Structured Output and Tools

## Goal

Build a tool registry with three tools, wire it to a model using function calling, validate tool arguments before execution, and handle parallel tool calls in a single turn.

## Why

Reliable tool calls are the prerequisite for agents — every agent loop depends on the model's output being parseable and the tool execution being safe.

## Steps

1. Define three tools using JSON Schema: a `calculate` tool (accepts an expression string, returns a number), a `search` tool (accepts a query string and returns a list of stub results), and a `read_file` tool (accepts a relative file path, returns file contents capped at 2000 characters).
2. Build a tool registry: a dictionary mapping tool names to their JSON Schema definition and their Python callable. The registry validates arguments against the schema before dispatch.
3. Implement the five-step function-calling loop:
   - Send the user message and tool definitions to the model.
   - Parse the model's `tool_use` block(s).
   - Validate each tool's arguments against the schema using a JSON Schema validator. Raise a clear error if validation fails — don't silently pass bad arguments to the function.
   - Execute the tool and collect the result.
   - Feed the result back to the model as a `tool_result` block and collect the final response.
4. Test with a prompt that triggers the `calculate` and `search` tools in parallel in a single turn (e.g., "What is 42 * 17, and search for 'retrieval augmented generation' simultaneously?"). Execute both concurrently.
5. Test with a prompt that triggers `read_file` on a path outside the current working directory — confirm the registry rejects it before the function runs.

## Done when

- A single turn with two tool calls executes both concurrently and returns the model's final answer.
- An invalid argument (wrong type or out-of-bounds path) raises a validation error before the function runs.
- The tool registry is a reusable class, not inline conditionals.
- The full five-step loop prints: the model's tool request, the validation result, the tool output, and the final model response.

## Stretch

Add a sixth step: tool-call authorization. Add an `allowed_tools` set to the registry. If the model requests a tool not in the set, return a `tool_result` block with an "unauthorized" error and continue the loop rather than crashing.
