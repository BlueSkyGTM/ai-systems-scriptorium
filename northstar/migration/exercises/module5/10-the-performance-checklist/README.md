# Exercise 10 — The Performance Checklist as a Runnable Audit

## Goal

Encode the curated performance checklist as a script that audits the `module5-serving/` stack and its host, classifies every item green / partial / skipped / open-finding with a reason, and emits a prioritized `FINDINGS.md` ranked by impact. Hardware-dependent checks degrade to `skipped` on a no-GPU host — never fake-green.

## Why

A checklist's whole value is a findings document a teammate can trust: what is green, what is honestly partial because the hardware can't exercise it, and what is an open finding worth fixing. The engineer who hands over *that* is worth more than the one who hands over a wall of checkmarks — the first told you where the bodies are; the second hid them. This exercise builds the audit that produces the trustworthy doc.

## Steps

1. **Audit harness.** Add `module5-serving/audit/checklist.py` with a `Check` abstraction: each check has a name, the bound it serves (`memory` / `compute` / `scheduling` / `io` / `host` / `telemetry` / `hardware`), a probe function, and returns a status — `green`, `partial`, `skipped`, or `open_finding` — plus a one-line reason and an impact rank. Keep it stdlib; the probes read config and the host, they do not run inference.

2. **Software probes (must produce real verdicts).** Implement probes that inspect the running stack and its config, e.g.:
   - **Scheduling:** is continuous-style batching enabled, or is the queue draining one request at a time? (Reuse the lesson-09 phase data if present.)
   - **Memory:** is the KV cache paged/block-wise with an eviction policy, or naive?
   - **Telemetry:** is a metrics recorder wired (the lesson-04 middleware), or is the stack flying blind?
   - **Version pinning:** are engine/config versions locked in a manifest, or floating?
   - **Goodput:** is an SLO declared and goodput computed, or only a mean reported?

   Each returns `green` / `open_finding` with the reason and a concrete remediation.

3. **Hardware probes (must degrade honestly).** Implement checks that need real hardware — `nvidia-smi topo -m` for NVLink topology, NVLink KV pooling, multi-GPU disaggregation, NUMA affinity, ECC, MIG/MPS. Probe for capability first (is there a GPU? is `nvidia-smi` present?). On a no-GPU host, return `skipped` with the reason `no GPU detected — cannot exercise`. **Never** return `green` for a check you could not actually run. If a GPU exists but only one, multi-GPU checks return `partial` (single-GPU host cannot exercise pooling/disaggregation).

4. **Do not disable the measurement.** If a probe cannot collect its evidence, that is a `skipped` or `open_finding` — the audit must never silently turn off a check to make the run look clean. Make this explicit: a check that errors out is an `open_finding` ("probe failed: ..."), not a pass.

5. **Rank by impact.** Order findings so the top runtime/cost contributors come first (the 80/20 rule), entered from the bound the stack's profile named — a memory-bound serving stack surfaces memory findings above host-tuning trivia. Hardware `skipped` items group at the bottom, clearly marked as capability-limited, not failures.

6. **Emit `FINDINGS.md`.** Write `module5-serving/audit/FINDINGS.md` grouped into: **green** (verified), **open findings** (ranked by impact, each with a remediation), **partial** (ran but capability-limited), and **skipped** (hardware absent, with the reason). The doc must be actionable cold — a teammate reads it and knows what to fix and what the host couldn't test.

## Done when

- `checklist.py` runs locally on a no-GPU laptop and emits `FINDINGS.md` without error.
- Software checks produce real `green` / `open_finding` verdicts against the actual `module5-serving/` config (e.g. flags missing telemetry or naive batching as ranked open findings).
- Every hardware-dependent check returns `skipped` (no GPU) or `partial` (single GPU) with an honest reason — none of them fake-green on a host that cannot run them.
- `FINDINGS.md` is grouped (green / open findings / partial / skipped), open findings are ranked by impact with remediations, and skipped items name the missing capability.
- A failed probe surfaces as an `open_finding`, never as a silently-passed or disabled check.

## Stretch

Add a `--ci` mode that exits non-zero if any `open_finding` exceeds a configured impact threshold, so the audit can gate a pipeline — and confirm that `skipped` (capability-limited) items never fail the gate, only true open findings do. This is the lesson's "guard every win" discipline turned into a regression gate.
