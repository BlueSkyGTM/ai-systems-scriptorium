# MCP Capabilities

Tools are the entry point. They're also just one of four things an MCP server can offer — and knowing the other three tells you when tools are the wrong choice.

## The full contract surface

MCP defines six primitives the spec calls capabilities: tools, resources, prompts, sampling, roots, and elicitation. Lesson 07 covered tools and transports. This lesson covers the rest. The distinction matters because these primitives solve different problems — reaching for a tool when you need a resource, or a resource when you need a prompt, produces clumsy code and confused models.

## Resources: read-only data the host pulls

A resource is data the MCP server exposes for context attachment — read-only, URI-addressed, pulled by the client when it wants to include the data in a model's context window. It is not a tool call. The model doesn't invoke it; the host application fetches it.

The resource primitive fits content the model should read but not compute: a file, a database record, a configuration snapshot, a recent-activity feed. Represent it as a resource, not a tool, when the answer is always the same for the same URI and producing it has no side effects.

```typescript
// module3-agent/mcp-server/index.ts (extending lesson 07)
server.resource(
  "agent-config",
  "config://module3-agent/config",
  async (uri) => ({
    contents: [{
      uri: uri.href,
      mimeType: "application/json",
      text: JSON.stringify({ model: "claude-opus-4-8", maxTurns: 10 }),
    }],
  })
);
```

Resources support subscription: the server sends a `notifications/resources/updated` message when a subscribed resource changes. The client re-fetches. This is how a live config feed or a watch-mode file diff surfaces to the host without polling.

Azure API Management can expose any REST API as an MCP server endpoint, converting each operation into a tool; the same gateway layer can surface read-only resource data — configuration snapshots, metadata — as context the agent pulls rather than computes. (learn.microsoft.com/azure/api-management/mcp-server-overview)

## Prompts: server-offered templates

A prompt is a reusable, parameterized conversation template the server offers to the host. The user or host application invokes it by name; the server returns a sequence of messages ready to insert into a model conversation. Think of it as a slash command with server-defined behavior.

The canonical use case: a notes MCP server offers a `review_note` prompt that takes a `note_id`, fetches the note content, and returns a structured review request — system message, note body, and a critique instruction — as a ready-to-send message list.

```typescript
server.prompt(
  "review-tool-schema",
  "Generate a review request for a tool's JSON Schema definition.",
  { tool_name: z.string() },
  async ({ tool_name }) => {
    const tool = registry.get(tool_name);
    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Review this tool schema for naming, description clarity, and parameter constraints:\n\n${JSON.stringify(tool?.parameters, null, 2)}`,
          },
        },
      ],
    };
  }
);
```

Prompts are the server's opinion on how to invoke its own domain knowledge. They are not tool calls — no side effects, no execution, just message construction. The host application presents them to the user and decides whether to send.

## Sampling: the server asks the host's model

Sampling inverts the usual direction. In a normal tool call, the host's model triggers a server action. In sampling (`sampling/createMessage`), the server sends a completion request to the host's model — without holding any API key or model credentials.

The use case: a server running a multi-step workflow (fetch files, identify which need summarization, summarize each) can offload the LLM steps to the host's model mid-execution. The server stays stateless on the model layer; the host retains control of which model is used and what it costs.

Sampling carries a safety requirement the spec makes explicit: the host **must** give the user the opportunity to review and approve any sampling request. A server that samples without user visibility is a covert agent loop — the model is running inside a server the user can't see. Build the approval path before you use sampling in production.

Azure AI Foundry Agent Service makes this approval requirement concrete: when a tool is marked `require_approval: always`, the agent pauses and returns an `mcp_approval_request` output item before executing — the host presents the request to a human, who approves or rejects it explicitly. The pattern applies equally to sampling: if a server is running model completions without user visibility, that is the failure mode the spec is designed to prevent. (learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol)

## Roots: scoped filesystem access

Roots tell the server which parts of the filesystem — or which URIs — the client is willing to expose. The client declares a list of root URIs (`roots/list`); the server must restrict its file operations to within those roots and reject out-of-bounds access.

Roots are a client-side declaration, not a server-side permission system. They shift the scoping responsibility to the party that owns the context: the host knows what the user's workspace contains; the server should not have to guess.

```json
// client declares roots during initialize
{"roots": [{"uri": "file:///Users/ray/module3-agent", "name": "module3-agent"}]}
```

The server enforces this by checking every file path against the declared roots before executing any read or write. A path outside the roots returns an error observation — the model can then report the restriction rather than silently fail.

## Elicitation: the server requests user input mid-execution

Elicitation lets a server pause a tool call and ask the user a structured question via the host UI — a form, a confirmation dialog, or (experimentally) a browser URL. The tool call does not complete until the user responds.

The canonical case: a tool about to delete a resource requests `elicitation/create` with a yes/no schema. The host presents the dialog. The user responds. The tool completes.

Elicitation is the escape hatch for tools that need human judgment in the middle of execution — not at the start (that's argument design), not at the end (that's the output). When a tool discovers mid-flight that it needs information only the user can supply, elicitation is the right primitive.

Keep elicitation rare. Every elicitation call blocks the tool and interrupts the user. Design tool arguments to request what the tool needs upfront; reach for elicitation only when discovery is genuinely impossible before execution starts.

## Async tasks and apps (one-line)

Two more extensions round out the surface: async tasks (SEP-1686) promote long-running tool calls to durable background jobs with a poll-for-result lifecycle; MCP apps (SEP-1724) return sandboxed interactive HTML from tool calls via the `ui://` resource scheme. Both are experimental extensions — note their existence; the exercise doesn't build them.

## The decision rule

Use a **tool** when the action has a result the model needs to reason with and may have side effects.
Use a **resource** when the data is read-only and URI-addressable — the host pulls it when it wants to include it in context.
Use a **prompt** when the server owns a reusable interaction template the host should offer as a command.
Use **sampling** when the server needs model completions but must not hold model credentials — and only with a user approval gate.
Use **roots** when the server accesses the local filesystem — always.
Use **elicitation** when a tool discovers mid-execution that only the user can supply a required piece of information.

Six primitives, one decision rule each — get them wrong and the server technically works but does the wrong thing. Get them right and the protocol does the composition for you.

## Core concepts

- MCP has six primitives: tools (computed actions with side effects), resources (read-only URI-addressed data), prompts (server-offered message templates), sampling (server-to-host model requests), roots (client-declared filesystem scope), and elicitation (mid-execution user input).
- Resources belong to data the host pulls for context; tools belong to actions the model triggers — conflating them produces wrong server designs.
- Sampling requires a user-visible approval path in the host; a server that samples without it is running a covert agent loop.
- Elicitation is the mid-execution escape hatch for tools that cannot know what they need until they start — keep it rare, because every call blocks and interrupts.

<div class="claude-handoff" data-exercise="exercises/module3/08-mcp-capabilities/">

**Build it in Claude Code** — extend the MCP server from lesson 07 with: a `config://module3-agent/config` resource returning the agent's runtime config as JSON; a `review-tool-schema` prompt template that builds a review message for any registered tool; and roots enforcement (reject any tool call that would access a path outside the declared roots). Verify with the Python MCP client: list tools, list resources, fetch the config resource, and get the prompt. Open the repo and run the exercise for this lesson.

</div>
