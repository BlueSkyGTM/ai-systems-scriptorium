# Module 5 — The Routing Layer — Build Plan

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN`).** Self-locked under Ray's "finish the job"
directive (decisions stated for override). Fifth authoring stage for Local Metal (M1-M4 shipped
2026-06-21). M5 is the first of the two portfolio modules: it wraps `ollama_client.py` (the M3 seed)
in a routing function that decides, per request, whether to serve locally or fall back to a cloud
model.

## The stage in one line

M3 built a client that calls the local model; M4 measured what local costs in latency and proved a
14B fits but a 32B does not. M5 turns that into a policy: every request carries signals (cost ceiling,
latency budget, context size, task sensitivity), and a router sends the cheap, simple, private, small-
context work to the local rig and escalates the hard, large-context work to a cloud model. Seam: the
rig only pays for itself if something decides when to use it; the router is that decision, and
`ollama_client.py` becomes the local arm of it. This is the artifact a hiring manager reads as "this
person can design a hybrid inference system," not just "this person installed Ollama."

## Settled decisions

1. **Stage = module.** Same shape as M1-M4; writes `build-log/local-metal/m5/output/{...}`.
2. **Held to the three contracts**; every worker brief carries them + the shipped M1-M4 lessons as the
   locked voice exemplar.
3. **The compounding spine pays off here.** `route.py` imports/wraps `ollama_client.py` (M3) for the
   local path; `LATENCY.md` (M4) is the data the routing thresholds are justified against. The repo
   now has a 5th document, `ROUTING.md` (the policy), gated by `check_routing.py`.
4. **Vendor-neutral routing.** Local = the Ollama rig; cloud = "a frontier model" (Claude as the
   reference) reached through the same OpenAI-compatible shape. The lesson teaches signals and a
   policy, not a specific SaaS router.

## Locked decisions (all accepted; stated for override)

1. **Throughline artifacts: `route.py` + `ROUTING.md` + `check_routing.py`.** `route.py` exposes a
   pure `route(request) -> Decision(target, reason)` policy function plus a live path that, when the
   decision is "local", calls `ollama_client.call()`. The pure policy is `--selftest`-checkable
   offline (deterministic decisions for a fixed set of sample requests), so the exercise is machine
   checkable with no rig and no cloud key.
2. **Routing signals: cost ceiling, latency budget, context size (tokens), task sensitivity
   (private/public).** A small, defensible set; thresholds recorded in `ROUTING.md`. Default policy:
   route to local when the request is small-context AND latency-tolerant OR privacy-sensitive;
   escalate to cloud when context exceeds the local model's window or the task is flagged high-stakes.
3. **Machine-checkable done-when without hardware/cloud:** `route.py --selftest` asserts the policy's
   decisions on a fixed request set (e.g. a private small request -> local; a 200k-context request ->
   cloud); `check_routing.py` gates `ROUTING.md` completeness + that every named signal has a
   threshold. No network in either.
4. **`ollama_client.py` reuse is real, not restated.** `route.py` imports it for the local call;
   the lesson shows the import and the wrap, and the selftest does not depend on it (pure policy),
   matching the M3/M4 offline-core + live-path pattern.
5. **Cloud is referenced, not required.** No cloud API key is needed to complete the module; the cloud
   arm is a stub the reader can wire to their own key. Keeps the module runnable and private-first.

## Proposed M5 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind |
|---|---------------|----------|------|
| 0 | `00-overview` | The rig pays off only when something decides when to use it; build the router that sends the right work local and escalates the rest. | concept |
| 1 | `the-routing-decision` | The signals that decide local vs cloud: cost, latency budget, context size, sensitivity; route cheap/simple/private local, hard/large escalate. | concept |
| 2 | `signals-and-thresholds` | Turn signals into a written policy with concrete thresholds; `ROUTING.md` as the policy record justified against the M4 latency baseline. | build |
| 3 | `build-the-router` | Build `route.py`: a pure `route(request)` decision function (offline-testable) that wraps `ollama_client.call()` for the local path. | build |
| 4 | `record-the-policy` | Record `ROUTING.md` and gate it with `check_routing.py`; the module's done-when. | build |

## Sources (three-source rule)

1. **Ingredient:** the SPEC + the shipped M3/M4 artifacts (`ollama_client.py`, `LATENCY.md`) + the
   `aipe` ore for serving/routing framing.
2. **External grounding:** hybrid/local-cloud routing patterns (model gateways, cost/latency/context
   signals), Ollama context-window (`num_ctx`) limits, frontier-model context windows and pricing as
   the escalation rationale; cite real URLs, capture to `vault/local-metal/m5-sources/PROVENANCE.md`.
   USE THE TOOLS (2 Haiku fetchers + MS-Learn where relevant).
3. **Editorial seam framing** in every lead.

## The fleet plan

Conductor-direct, tiered: 2 Haiku source-fetchers (routing patterns + signals; context/pricing) feeding
4 Sonnet lesson authors. Conductor writes the overview, owns + tests `route.py` + `check_routing.py`
(byte-identical to ship), reviews, reconciles, runs the gates.

On ship: VERIFY (voice + grounding), BUILD/TEST (`mdbook build` + `route.py --selftest` +
`check_routing.py`), then `GATE-APPROVE-SHIP` (cleared under "finish the job"), commit + push.
