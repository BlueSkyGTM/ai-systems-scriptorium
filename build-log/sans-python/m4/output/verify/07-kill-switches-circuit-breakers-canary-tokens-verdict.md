# VERIFY verdict — Lesson 07: Kill Switches, Circuit Breakers, Canary Tokens

**Lesson:** `build-stages/m4/output/author/07-kill-switches-circuit-breakers-canary-tokens.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch02 Op-Safety, safety-critical)
**Date:** 2026-06-19

## Markers resolved (1 of 1)

| Marker | Source checked | Result |
|---|---|---|
| `[verify: Cilium / eBPF — egress redirection / network policy at the kernel layer]` | WebSearch Cilium docs (Local Redirect Policy, egress gateway, eBPF datapath / TC hooks) | **PASS → removed.** Cilium's eBPF/BPF datapath enforces and redirects pod egress in-kernel before the packet leaves the node (local redirect policy → node-local backend; egress gateway; TC hooks govern all egress). Reworded to describe the verified mechanism precisely; the "forensic honeypot" remains an applied engineering use of redirection (framed as such), not a documented Cilium feature name. |

## Claim ledger

| Claim | Source | Verdict |
|---|---|---|
| Kill switch = boolean the agent reads but cannot write (feature flag / Redis key / signed config / container kill) | Ph15 L14 verbatim ("boolean the agent reads but cannot write — feature flag, Redis key, signed config, container kill") | PASS |
| Switch must live outside the agent's blast radius; read-only access-control rule is load-bearing | Ph15 L14 + L13/L14 spine; LaunchDarkly/Statsig/Unleash named in source | PASS |
| Circuit breaker = Nygard pattern; closed/open/half-open | Ph15 L14 verbatim ("circuit breaker (closed/open/half-open)"; "Nygard circuit breakers") | PASS |
| Behavioral trip: N identical tool calls in a row (five) | Ph15 L14 verbatim ("trips on patterns like five identical tool calls") | PASS |
| Statistical detectors (EWMA/CUSUM) layer on top of hard limits, never replace | Ph15 L14 verbatim ("statistical detectors (EWMA/CUSUM) must be layered with hard constitutional limits that do not bend") | PASS |
| Canary token = fake credential / honeypot record an agent has no legit reason to touch, alarms on access | Ph15 L14 verbatim ("fake credential or honeypot record an agent has no legitimate reason to touch") | PASS |
| eBPF/Cilium quarantine: reroute egress to a forensic honeypot at the kernel layer | Ph15 L14 ("eBPF/Cilium can rewrite a quarantined pod's egress to a forensic honeypot at the kernel layer") + Cilium docs (mechanism confirmed) | PASS |
| Budget governor (L06) is the 4th control plane member; its breach trips the switch | de-dup thread to L06 | PASS |
| Control plane defined once for one agent, inherited by the fleet | PLAN de-dup rule (kill-switch defined L06–07, referenced at fleet scale) | PASS |
| `kill_switch.py` / `breaker.py` code | Self-consistent illustrative control-plane code; the read-only Redis ACL caveat is explicit and correct | PASS |

## STYLE result — PASS

- Single H1, present tense, 2nd person, one voice. ✓
- Lead: states the problem (the how of halting + detectors) with a strong hook ("a thing that can now read its own off switch"). Seam (old reliability engineering reasserted for agents = MLOps-meets-AI control plane) is clear; mid-chapter, the explicit cusp sentence is carried by L05/L06 and not forced here, avoiding §8 monotony. ✓
- One `## Core concepts` block, 4 testable propositions. ✓
- Handoff div well-formed. ✓
- Ending ("Keep the off switch in your hand, not the agent's"): directive/warning shape, not the banned template; varied vs. siblings. ✓
- Acronyms: ACL now expanded at first prose use ("access-control rule (ACL)") — FIXED. EWMA/CUSUM glossed by role; eBPF a standard product-category name. ✓
- De-dup: budget governor referenced to L06; fleet scale deferred ("referenced there, defined here"). ✓

## Antilibrary fence — PASS
No frontier-safety/policy material. ✓

## Overall verdict: **PASS** (1 marker resolved, 1 minor STYLE fix [ACL expansion], 0 FLAGGED). Ship-ready.
