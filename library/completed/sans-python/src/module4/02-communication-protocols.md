# Communication Protocols (MCP / A2A / ACP / ANP)

Two agents that talk by passing raw strings will, eventually, lie to each other. One emits "done — see results above," the other parses "results" from the wrong field, and the bug surfaces three steps later as a confident wrong answer. The fix is a wire contract: a typed, discoverable, addressable format that makes a handoff checkable instead of hopeful — and in 2026 that contract is a four-layer protocol stack you should be able to read top to bottom.

## You Build a Real Agent-to-Agent Handoff

You build a handoff where one agent discovers another's tools over MCP and delegates a task to it over A2A — a typed wire message, not a string shoved into a prompt. The point is to feel the difference between "I told the other agent what I wanted" and "I sent it a message that either validates or fails loud."

## The Stack, as Four Layers

The 2026 protocol sprawl looks like alphabet soup until you stack it by what each layer addresses. Each expands on first use; hold the four.

**MCP — Model Context Protocol.** The vertical link: agent to *tools*. An agent connects to an MCP server, lists the tools it exposes with `tools/list`, reads their input schemas, and invokes them with `tools/call` over JSON-RPC. You built this in Module 3. It answers *what can I call, and how.*

**A2A — Agent-to-Agent.** The horizontal link: agent to *agent*. Where MCP is an agent reaching down to tools, A2A is an agent reaching across to a peer. It defines an Agent Card for discovery (published at a well-known path, `/.well-known/agent-card.json`), a Task with an explicit lifecycle (`submitted → working → completed / failed / canceled`, plus `input-required` when the peer needs more from you), and typed Artifacts as results. The client sees state transitions, not the peer's internals.

**ACP — Agent Communication Protocol.** The enterprise layer: runs, trajectories, audit metadata. When an agent's work has to be replayable and accountable — who called what, in what order, with what result — ACP carries the structured record that compliance and debugging both read.

**ANP — Agent Network Protocol.** The trust layer: decentralized identity (DID) and verifiable trust between agents that have never met. When agents span organizations, "is this peer who it claims to be" stops being assumable, and ANP is where that gets answered.

Read bottom to top: discover and call tools (MCP), delegate to peers (A2A), audit the runs (ACP), trust strangers (ANP). Most systems you build live in the bottom two. The top two matter the moment your fleet crosses a team or company boundary.

## The Heritage: Which "Innovations" Are Reinventions

Here is the thing the announcements won't tell you. Almost none of this is new.

In 2002 the FIPA standards bodies published FIPA-ACL — an Agent Communication Language with twenty-two performatives (`request`, `inform`, `propose`, `agree`, `refuse`...), content languages, and named interaction protocols including contract-net for task delegation. (The IEEE Computer Society later took FIPA over in 2005, which is why you sometimes see it cited as an IEEE standard.) It traced back through KQML in the early 1990s to speech-act theory: the philosophical observation that an utterance is itself an action — to *request* is to do something, not just say something. FIPA had a reference platform in JADE, and it faded around 2010 when the web won and XML agents lost.

Look at A2A's task lifecycle and you are looking at FIPA's contract-net with JSON instead of XML and a natural-language ontology instead of a formal one. The performatives came back as task states. The content language came back as typed Artifacts. This is not a criticism — JSON-native and LLM-native are genuine improvements — but it is leverage. Knowing the heritage tells you which marketed "innovations" are reinventions, and warns you which old failure modes the new specs will rediscover: ambiguous performatives, deadlocked negotiations, ontology mismatch between teams. The 1990s agent community hit all three. So will you.

## Why Raw Strings Fail

Skip the protocol and pass strings, and three failures are waiting.

**Misinterpretation.** "Process the file and return the summary" — which file, what format, summary of what. A typed message names the task, the input, and the expected artifact type. A string leaves all three to the reader's guess, and an LLM guesses confidently.

**Deadlock.** Agent A waits for B; B is waiting on a clarification A never knew to send. With no task lifecycle, neither knows the other is stuck. A2A's explicit states — `working`, `failed`, `canceled` — make a stall visible instead of silent.

**Scale.** Two agents you wrote can share a private convention. Ten agents from four teams cannot. The contract is what lets a team you've never met delegate to your agent without a meeting — the Agent Card *is* the meeting.

## Reuse the M3 Wire Contract

You already typed an MCP message in Module 3 — the TypeScript `tools/call` request and result, schema-validated end to end. Reuse it. MCP for tool discovery stays exactly as you built it; A2A is the new piece, and it rhymes. The Agent Card is a typed manifest like an MCP tool schema. The Task is a typed request like a `tools/call`. Type the A2A wire format the same way you typed MCP: a schema the sender fills and the receiver validates, so a malformed handoff fails at the boundary instead of three steps downstream. Control plane stays Python; the wire contract is the place a strong type earns its keep, so it stays TypeScript.

```typescript
// A2A: a typed task message, not a string in a prompt.
interface A2ATask {
  id: string;
  method: "message/send";          // the A2A spec's send-a-message RPC
  params: {
    skill: string;                 // matches a skill on the peer's Agent Card
    input: { mimeType: string; content: unknown };
  };
}

type A2AState = "submitted" | "working" | "completed" | "failed" | "canceled";

interface A2AResult {
  id: string;
  state: A2AState;
  artifacts: { mimeType: string; content: unknown }[];  // typed, not free text
}
```

The receiver validates `skill` against its own Agent Card and the input against the skill's schema. A mismatch is a `failed` state with a reason, returned at the wire — not a wrong answer three turns later that you spend an afternoon tracing.

## The Seam This Sits On

A protocol is where the AI Engineer's question (can these agents coordinate at all) meets the MLOps question (is every handoff typed, discoverable, and auditable). String-passing fails both: it can't scale the coordination and it can't be audited. Type the wire and you've made the seam's two halves agree — the agents talk, and you can prove what they said.

## Core Concepts

- The four-protocol stack layers by concern: MCP (agent ↔ tool discovery and invocation), A2A (agent ↔ agent delegation via Agent Cards and a task lifecycle), ACP (enterprise audit and trajectory metadata), ANP (decentralized identity and trust).
- Today's agent protocols are largely a JSON-native, LLM-native rehash of FIPA-ACL (2000) and KQML (1993); knowing the heritage tells you which "innovations" are reinventions and which old failure modes — ambiguous performatives, deadlock, ontology mismatch — the new specs will rediscover.
- Passing raw strings between agents fails on misinterpretation, deadlock, and cross-team scale; a typed wire contract makes a bad handoff fail loud at the boundary instead of producing a confident wrong answer downstream.

<div class="claude-handoff" data-exercise="exercises/module4/02-communication-protocols/">

**Build It in Claude Code** — in `module4-fleet/`, give the two harness agents a real wire-format handoff: the supervisor discovers the worker's skills via an Agent Card and delegates a task over a typed A2A message, reusing your Module 3 MCP types for the wire contract. Prove a malformed handoff fails at the boundary, not downstream.

</div>
