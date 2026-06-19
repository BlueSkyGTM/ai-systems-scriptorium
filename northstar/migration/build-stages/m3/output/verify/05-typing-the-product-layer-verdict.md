# Verdict: 05-typing-the-product-layer

## Markers resolved

**Marker 1** — `[MS-Learn: Azure AI Agents — TypeScript generic tool definitions and ToolDefinitionUnion for typed agent function calling]`
- Query: "Azure AI Agents ToolDefinitionUnion TypeScript"
- Validated by: https://learn.microsoft.com/javascript/api/@azure/ai-agents/tooldefinitionunion?view=azure-node-latest — `ToolDefinitionUnion` is a discriminated union of `FunctionToolDefinition | CodeInterpreterToolDefinition | FileSearchToolDefinition | BingGroundingToolDefinition | AzureAISearchToolDefinition | OpenApiToolDefinition | ConnectedAgentToolDefinition | AzureFunctionToolDefinition | ToolDefinition`. This confirms the lesson's point about generic tool wrappers mapping to the SDK's union type.
- Action: Marker deleted. Replaced with a grounded clause: "In `@azure/ai-agents`, `ToolDefinitionUnion` is exactly this pattern — a discriminated union of `FunctionToolDefinition | CodeInterpreterToolDefinition | FileSearchToolDefinition | …` keyed on `type` (see learn.microsoft.com/javascript/api/@azure/ai-agents/tooldefinitionunion)."

**Marker 2** — `[MS-Learn: Azure AI Agents — TypeScript agent and MCP tool interface contracts in the @azure/ai-agents SDK]`
- Query: "Azure AI Agents Agent interface tools ToolDefinitionUnion CreateAgentOptionalParams"
- Validated by: https://learn.microsoft.com/javascript/api/@azure/ai-agents/agent?view=azure-node-latest (`tools: ToolDefinitionUnion[]` on the `Agent` interface); https://learn.microsoft.com/javascript/api/@azure/ai-agents/createagentoptionalparams?view=azure-node-latest (`tools?: ToolDefinitionUnion[]`); https://learn.microsoft.com/javascript/api/@azure/ai-agents/updateagentoptionalparams?view=azure-node-latest (`tools?: ToolDefinitionUnion[]`). Index-signature map claim confirmed.
- Action: Marker deleted. Replaced with a grounded clause naming the SDK interfaces explicitly.

**Marker 3** — `[MS-Learn: TypeScript declaration files — acquiring types from DefinitelyTyped and authoring .d.ts for untyped modules]`
- Query: "TypeScript declaration files DefinitelyTyped authoring .d.ts untyped modules"
- Validated by: https://learn.microsoft.com/visualstudio/ide/javascript-intellisense?view=visualstudio#automatic-acquisition-of-type-definitions — confirms DefinitelyTyped as the primary repository for `.d.ts` files and the auto-acquisition pattern. The `declare module` pattern is standard TypeScript (not a distinct MS Learn article, but the DefinitelyTyped integration is confirmed).
- Action: Marker deleted. Replaced with a light clause grounding the DefinitelyTyped pattern in the VS/VS Code tooling context.

**Marker 4** — `[MS-Learn: TypeScript type operators — keyof, typeof, and as const for deriving agent tool parameter types]`
- Query: "TypeScript keyof typeof as const deriving types agent parameter"
- Validated by: https://learn.microsoft.com/javascript/api/@azure/msal-common/granttype — `type GrantType = (typeof GrantType)[keyof typeof GrantType]`; https://learn.microsoft.com/javascript/api/@azure/msal-common/aadauthorityconstants — same `(typeof X)[keyof typeof X]` idiom. Pattern is live in production Azure SDKs, not just a TypeScript language feature in isolation.
- Action: Marker deleted. Replaced with a clause showing the idiom in real Azure SDK code, which is more useful than a generic TypeScript docs reference.

**All 4 markers: RESOLVED**

## SDK shape verifications

- **`ToolDefinitionUnion`:** Confirmed. Union type in `@azure/ai-agents` with discriminant `type` on each member. Lesson's description of the generic wrapper mapping to this union is accurate in concept.
- **`FunctionToolDefinition` in lesson 05:** Lesson 05 does not directly claim a top-level shape match (unlike lesson 04). It references `ToolDefinitionUnion` as a discriminated union keyed on `type` — this is accurate.
- **Declaration merging and `@azure/ai-agents`:** The lesson's `AgentContext.mcpSessionId` example is illustrative (TS language feature), not a claim about a specific SDK interface. No correction needed.
- **`claude-opus-4-8` model ids:** Left as-is per instructions (validated).

## §4 Ending rewrite

**Ending (was):** "An AI Platform Engineer who builds this layer controls the schema boundary — every model-generated argument, every MCP tool call, every agent-state transition passes through types the compiler already checked."
- Uses the banned "An AI Platform Engineer who…" template.

**Ending (now):** "Without this layer, schema drift is silent — a renamed tool key in the registry and an outdated parameter name in the schema have nothing to catch them until the model calls the wrong function at runtime."
- Shape: cost / warning. Names the concrete failure mode (silent schema drift → wrong function call at runtime). Different shape from lesson 04's ending (consequence of tsc-as-reviewer) — no two endings alike.

## STYLE conformance

- **§1 Unity:** PASS — second person, present tense, practitioner POV. Voice consistent with lesson 04 and the module throughline.
- **§2 Simplicity:** PASS — no qualifiers added in edits; replacement clauses are concrete and active.
- **§3 One idea:** PASS — lesson teaches one concept: turning a single typed tool into a typed product layer using generics, interfaces, declaration files, and type modifiers.
- **§4 Lead + ending:** PASS — lead establishes the scale shift from one tool to a fleet; ending replaced, warning shape, earns the click by naming what breaks without the layer.
- **§5 Core concepts:** PASS — four propositions, each one sentence, each testable. The `as const` + `keyof` + `typeof` concept links correctly to the MSAL SDK idiom now verified.
- **§8 Variety:** PASS — lesson has natural rhythm variation from short declaratives through longer code-block explanations. The `as const` / `keyof` / `typeof` section builds momentum across three named operators, then cuts to "These three work together" — good rhythm. One forward-pointer paragraph (mapped types in Module 4) adds a longer, breathing sentence. No human moment — same note as lesson 04, flagged for editor consideration, not a block.

**VERDICT: PASS**
