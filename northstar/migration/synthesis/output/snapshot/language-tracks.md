# Rust & TypeScript — Threading Map

The two non-AI-native sources (`100-exercises-to-learn-rust`, `typescript-projects` / *Learning
TypeScript*). Everything else in the library teaches a concept already inside an AI context; these
teach a language. **Decision: thread them to point-of-use, no front-loaded wall.** Teach only enough
to break into the field; pull each deeper topic forward to the first AI task that demands it; the rest
is antilibrary.

Why threaded and not walled: the thesis is a *sequencing* argument. Front-loading a full Rust course
and a full TS course in Module 1 rebuilds the exact prerequisite wall Sans Python exists to kill — just
in different languages. The extraction's per-topic "Sans-Python use case" / "Why it matters" notes are
a **map of attachment points** — each language topic already names the AI task it serves.

Archetype fit (from SPEC.md): **TypeScript = Build / product layer** (agents, tools, APIs). **Rust =
Deploy / serving layer** (inference, CLIs, async pipelines). So TS depth attaches earlier (agent-building,
M3) and Rust depth later (serving, M5) — naturally, by where each language is used.

---

## TypeScript — pure thread (additive)

**Entry: Module 3 (Agent Foundations)** — the first place product-layer code gets written (typed tools,
MCP servers). TS type features are additive, so there's no concentrated block: introduce the break-in
set at entry, thread the rest.

**Break-in set (taught at M3 entry, minimal):** The Type System · From JavaScript to TypeScript ·
Unions & Literals · Objects · Functions · basic Interfaces · Configuration (tsconfig) · Using IDE Features.
→ *"read and write typed TS, define a typed tool, run `tsc`."*

**Point-of-use threads:**

| TS topic | Attaches at | AI task that pulls it |
|----------|-------------|------------------------|
| Generics | M3 | reusable typed tool wrappers `Tool<TInput,TOutput>` |
| Interfaces (index sigs, declaration merging) | M3 | MCP server contracts / agent schemas |
| Type Modifiers (`keyof`/`typeof`/`as const`) | M3 | derive tool-param names, agent-state enums |
| Declaration Files (`.d.ts`) | M3 | typing untyped/JS-first LLM packages |
| Classes | M3 | agent / tool class scaffolding |
| Type Operations (mapped/conditional/template-literal) | M4 | schema-derived types for multi-agent contracts (advanced) |
| Syntax Extensions (decorators) | as-needed | declarative agent/tool classes |

**Antilibrary:** enums/namespaces, deep type-operation corners, and any type-system feature no
agent/tool/serving lesson demands.

---

## Rust — one on-ramp, then thread

**Entry: Module 5 (Deploy & Performance Engineering)** — the serving layer, CLIs, async. Some threads
reach back into Module 4 (concurrent agent tasks). Rust's ownership model is irreducible, so it gets a
**small concentrated on-ramp** (not dripped), then threads like TS.

**On-ramp (concentrated, ~3–4 lessons at Rust entry):** Intro (syntax, `fn`, types) · Basic Calculator
(integers, control flow, loops) · **Ticket v1 core (structs, ownership, borrowing, stack/heap)**.
→ *"you understand ownership and can write basic Rust."* This is the one allowed concentrated block,
because ownership is a gestalt you need whole before any real Rust.

**Point-of-use threads (after the on-ramp):**

| Rust topic | Attaches at | AI task that pulls it |
|------------|-------------|------------------------|
| Ticket v2 (enums, `Result`, error handling, `thiserror`, `TryFrom`) | M5 | typed error handling in serving / CLI tooling |
| Traits (bounds, `From`, `Deref`, derive) | M5 | generic serving components, typed schemas |
| Ticket Management (collections, iterators, lifetimes, slices, `HashMap`) | M5 | data processing in serving pipelines |
| Threads (`Arc`/`Mutex`/channels, `Send`/`Sync`) | M4 / M5 | concurrent agent task pools, parallel serving |
| Futures (`async`/`.await`, `tokio`, spawn, cancellation) | M5 (+ M4) | async serving, streaming, async tool calls |

**Antilibrary:** Rust topics no serving/CLI/async AI task in this curriculum demands.

---

## The medium note (Build-phase implication)

The extracted source lessons are predominantly **Python** (aefs is Python-from-scratch). Under the thesis,
the *writing* shifts to TS (product) and Rust (serving). So threading works because, at each language's
point-of-use, the relevant AI lessons get authored/ported into that language. This is a lesson-authoring
(Step 4 / Build) directive, recorded here so the build spec carries it: TS lessons land where product-layer
work is written in TS (M3+); Rust lessons land where serving work is written in Rust (M5, some M4).

---

## Open sub-decisions (Ray to ratify)

1. **Rust on-ramp size** — recommend a small concentrated 3–4 lesson block (basics + ownership) at Deploy
   entry, vs pure drip. (Recommended: small block — ownership is irreducible.)
2. **TS entry = M3** — assumes M2 (LLM Engineering) building stays Python-literacy/English, and TS arrives
   when you build the first agent/tool. Alternative: pull TS entry into M2 if LLM-app building is authored
   in TS. (Recommended: M3 entry, matches snapshot edges + Build-archetype.)
