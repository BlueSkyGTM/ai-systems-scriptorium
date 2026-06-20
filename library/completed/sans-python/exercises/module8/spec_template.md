# Final Exam — Task Spec

Fill this in. It is the contract you point the M7 governed fleet at. The driver
(`run_exam.py`) reads the `**Field:**` lines and the `## Acceptance criteria`
list; the rubric (`rubric.py`) grades the run against them. An empty field is a
missing answer — the rubric marks it.

**Track:** <one of: eval-gated-ci-cd | multi-tenant-rag | agentic-system>

**Reference architecture:** <a Ch16 case study, e.g. "#18 Eval-Gated CI/CD for an AI Product" — see 02-reference-architectures.md>

**Version:** <semver of this exam artifact, e.g. 1.0.0>

**Feature:** <the one feature the fleet ships, in a few words — the `ship_feature` input>

**Business problem:** <one line: why this system exists and who it serves. This is your README framing.>

## Acceptance criteria

State the bar you will judge the produced system against. These are *your* tests —
the rubric requires at least one, and the produced run must clear the system's
acceptance suite to pass R1/R2.

- <e.g. the acceptance suite passes (the fleet's verify gate ACCEPTs)>
- <e.g. the run stays under the team budget cap>
- <e.g. the cross-agent audit answers all four accountability clauses>
- <add the criteria specific to the version of the architecture you scoped>

## What "a version of" means here

You are not inventing an architecture and you are not cloning a FAANG system. You
scope *a version of* the reference architecture small enough that the M7 fleet can
ship it on the offline gate, while keeping the seam that makes it that architecture
(the eval gate, the tenant isolation boundary, the agent loop). Name the seam you
keep and the scope you cut in the business-problem line.
