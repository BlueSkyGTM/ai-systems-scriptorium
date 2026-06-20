# Verdict: 04-typescript-break-in

## Markers resolved

**Marker 1** — `[MS-Learn: TypeScript tsconfig strict mode and noImplicitAny for Azure SDK projects]`
- Query: "TypeScript tsconfig strict mode noImplicitAny Azure SDK projects"
- Validated by: Multiple Azure AI SDK quickstarts on Microsoft Learn use the identical tsconfig shape: `"strict": true`, `"module": "NodeNext"`, `"target": "ES2022"` (e.g., learn.microsoft.com/azure/foundry/openai/whisper-quickstart, learn.microsoft.com/azure/ai-foundry/openai/use-your-data-quickstart, learn.microsoft.com/azure/search/search-get-started-text). Claim fully grounded.
- Action: Marker deleted. Replaced with a light grounding clause: "Azure SDK quickstarts use this same `tsconfig.json` shape — `"strict": true`, `"module": "NodeNext"`, `"target": "ES2022"` — across every TypeScript SDK sample on Microsoft Learn."

**Marker 2** — `[MS-Learn: Azure AI Agents — FunctionToolDefinition interface and function calling with TypeScript]`
- Query: "Azure AI Agents FunctionToolDefinition interface function calling TypeScript"
- Validated by: https://learn.microsoft.com/javascript/api/@azure/ai-agents/functiontooldefinition?view=azure-node-latest — `FunctionToolDefinition` exists in `@azure/ai-agents`, extends `ToolDefinition`, with `type: "function"` and `function: FunctionDefinition`. `FunctionDefinition` holds `name`, `description`, `parameters` (see learn.microsoft.com/javascript/api/@azure/ai-agents/functiondefinition).
- SDK shape fix required: The lesson claimed `FunctionToolDefinition` "follows the same shape — name, description, parameters as JSON Schema, a handler." This is inaccurate: those fields are nested one level deeper inside the `function: FunctionDefinition` property, not at top level. Lesson softened per instructions: "Production agent SDKs use this same shape… (In `@azure/ai-agents`, `FunctionToolDefinition` nests these under a `function: FunctionDefinition` property; the concept is identical, the path is one level deeper.)"
- Action: Marker deleted. Prose corrected to soften the direct shape-match claim.

**Marker 3** — `[MS-Learn: TypeScript compilerOptions — strict mode, declaration files, and NodeNext module resolution]`
- Query: "TypeScript compilerOptions strict mode declaration files NodeNext module resolution"
- Validated by: Same quickstart pages as Marker 1 confirm `strict`, `NodeNext`, `moduleResolution: NodeNext` as the standard baseline. `declaration: true` is a standard `tsc` option (TypeScript docs); no separate MS Learn page needed beyond what is already cited.
- Action: Marker deleted. Replaced with a light grounding clause referencing the Microsoft Learn pattern.

**All 3 markers: RESOLVED**

## SDK shape corrections

- **`FunctionToolDefinition` shape:** The `@azure/ai-agents` SDK's `FunctionToolDefinition` does NOT expose `name`, `description`, `parameters` at the top level. It exposes `type: "function"` (inherited from `ToolDefinition`) and `function: FunctionDefinition`. `FunctionDefinition` is the nested object with `name`, `description`, `parameters`. The lesson's direct equivalence claim was wrong. Fixed by softening to "production agent SDKs use this shape" and adding an accurate parenthetical about the real nesting.
- **`ToolDefinitionUnion`:** Confirmed — exists in `@azure/ai-agents` as a discriminated union of `FunctionToolDefinition | CodeInterpreterToolDefinition | FileSearchToolDefinition | BingGroundingToolDefinition | AzureAISearchToolDefinition | OpenApiToolDefinition | ConnectedAgentToolDefinition | AzureFunctionToolDefinition | ToolDefinition`. The lesson's core concept about the discriminated-union pattern is correct in concept. Updated core concept to name the specific member types for accuracy.
- **`claude-opus-4-8` model ids:** Left as-is per instructions (validated).

## §4 Ending rewrite

**Ending (was):** "An AI Platform Engineer who can read, write, and compile typed TypeScript owns the seam between the model's untyped world and the typed contracts the product layer enforces."
- Uses the banned "An AI Platform Engineer who…" template.

**Ending (now):** "The compiler is now the first reviewer — every tool call the model generates has to pass `tsc` before it reaches your business logic."
- Shape: consequence. Names the mechanism (tsc as first reviewer) and the stake (business logic protection). Earns the click.

## STYLE conformance

- **§1 Unity:** PASS — second person, present tense, practitioner POV throughout. Voice confident and blunt.
- **§2 Simplicity:** PASS — no qualifiers introduced in edits; active voice maintained; all three clauses replacing markers are concise.
- **§3 One idea:** PASS — lesson teaches one concept: typed TypeScript as the compiler-enforced contract between model and tools.
- **§4 Lead + ending:** PASS — lead is sharp (starts mid-action: "The agent loop you built…"); ending replaced, consequence shape, no template.
- **§5 Core concepts:** PASS — four propositions, each one sentence, the `ToolDefinitionUnion` concept updated to name member types accurately.
- **§8 Variety:** NOTE — lesson has a moderate run of short declaratives in "The type system in three minutes" section. This is acceptable because the section intentionally cycles through three building blocks (primitive / union / object) with code examples breaking the rhythm. One human moment would strengthen this lesson; there is none currently. Flagged for editor consideration — not a block.

**VERDICT: PASS**
