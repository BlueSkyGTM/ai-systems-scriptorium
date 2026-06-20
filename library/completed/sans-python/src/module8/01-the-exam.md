# The Exam

Every module before this one handed you a part. This one hands you the job. You do not build a new artifact for the final; you take the governed fleet you already shipped, point it at a production-grade problem, and prove you can run it like the infrastructure it is.

## What the Exam Is

The exam is one task with three jobs inside it. Pick a track. Point the Module 7 governed fleet at a real reference architecture and have it ship *a version of* that system. Then operate the fleet and judge what it built. The first job is design, the second is operations, the third is acceptance — and the grade is the same one a hiring manager gives a portfolio: does this run, is it governed, would you put it near production?

What the exam is *not* matters as much. It is not a fresh agent build. You wrote the agents in Module 6 and governed them into a fleet in Module 7; rewriting either is a sign you have misread the assignment. It is also not blank-page architecture. You do not invent a system from nothing — you replicate a known one, scoped down, with its load-bearing seam kept intact. The blank page is where weak portfolios go to die; the strong ones build a recognizable version of a real architecture and get it running.

## The Three Tracks

You choose one of three, and each is anchored to specific case studies from the catalog in the next chapter.

- **Eval-gated CI/CD.** A pipeline that ships a model change only when a statistical eval gate clears — golden sets, failure-mode taxonomies, a canary. The seam is the gate: nothing promotes without passing it.
- **Multi-tenant RAG.** A retrieval system serving many tenants from shared infrastructure, with isolation that holds under load. The seam is the tenant boundary: tenant A never sees tenant B's data, by construction.
- **Agentic system.** A system whose work is done by an agent loop — an autonomous coding agent, a multi-agent support desk, a computer-use agent, an MCP knowledge agent. The seam is the loop: plan, act, observe, gated, under a human.

You pick the track, then pick the architecture under it, then scope the version you can ship. The track names the shape of the problem; the case study gives you a real design to replicate instead of one to invent.

## "Build a Version of," Not Blank-Page

The instruction is precise, so read it twice: build *a version of* a real architecture. Not a clone of a hyperscaler's system — you do not have their traffic or their team. Not a toy that drops the thing that makes it that architecture — a multi-tenant RAG without isolation is just RAG. A version is the smallest system that still has the seam. You cut the scale and keep the spine.

This is the discipline that separates an engineer from a tinkerer. A tinkerer starts from nothing and reinvents a worse wheel. An engineer reads how the problem was already solved, takes the pattern, and adapts it to the budget in front of them. The catalog hands you twenty solved problems. Your work is to choose one, name the seam you must keep, declare the scope you will cut, and write that down as the task spec the fleet runs.

## The Fleet Builds; You Operate and Judge

Here is the division of labor, and it is the whole point of the exam. The fleet does the building. The architect decomposes your feature into slices, two coders implement them in parallel as the Module 6 loop, the tester runs the acceptance suite for a deterministic verdict, and the reviewer gates the merge. That is five agents doing the work you would otherwise do by hand.

Your job sits on top of theirs. You are the operator: you configure the registry and the budgets, you work the human-in-the-loop (HITL) inbox to approve or reject the merge, you read the cross-agent audit after the run, and you hold the kill switch. You are the judge: you grade the produced system against an acceptance rubric, by criterion, not by vibe. And you are the architect-of-record: when it fails, you are the one who says why and what changes. The fleet is the substrate, the task spec is the input, and your judgment is the grade.

This is the AI Platform Engineer's job. The engineers who lose it try to do the agents' work for them — micromanaging the loop, hand-editing the diffs. The ones who keep it run the fleet as infrastructure: set the policy, watch the gates, intervene on breach, and stay accountable for every action the system takes.

## The Terminal Node of the Compounding Arc

The book has been building one structure the whole way, and this is its last node. You built a single agent and made it verifiable — "done" became a fact from running tests, not a claim. You governed that agent with a budget, a kill switch, and a human gate. You composed the controls into a fleet. You wrapped the fleet around the agents, and the result shipped software. Now you point that result at a production system and run it.

Single agent → team → governed fleet → production system, operated and judged. Nothing in that chain was busywork; each link is load-bearing for the next. The coding agent you made verifiable in Module 6 is the reason the reviewer can trust a coder node in Module 7, which is the reason you can govern the fleet in Module 8 at all. The exam is not a new mountain. It is the summit of the one you have been climbing — and the proof you can stand on it.

## What You Build

You build a task spec and operate a fleet against it. You choose a track and a reference architecture from the twenty case studies, scope *a version of* it that keeps the seam, and write the spec: the track, the architecture, the feature the fleet ships, the business problem, and the acceptance criteria. Then you point the shipped Module 7 governed fleet at that spec, operate it under the console — set the budgets, work the HITL inbox, read the audit, hold the kill switch — and grade the produced system against a seven-criterion acceptance rubric. The fleet builds the system; you run it as infrastructure and judge it. The exam harness ships with a worked example: the fleet ships a version of an autonomous coding agent against a sample spec, offline, and the rubric grades the run pass/fail by criterion.

## Core Concepts

- The final exam is not a new build but an operation: you point the shipped Module 7 governed fleet at a production problem, and the grade is whether you can run it as infrastructure and judge what it ships.
- "Build a version of" means replicate a real reference architecture scoped down to its load-bearing seam — not clone a hyperscaler, and not invent from a blank page, which is where weak portfolios fail.
- The fleet does the building; you do the operating and the judging — operator, judge, and architect-of-record — and that division of labor is the AI Platform Engineering job itself.
- The exam is the terminal node of the compounding arc: single agent → team → governed fleet → production system, each link load-bearing for the next.

<div class="claude-handoff" data-exercise="exercises/module8/">

**Build It in Claude Code** — operate the fleet and judge the system. Open the exam exercise. Read `spec_template.md` and `02-reference-architectures.md`, choose a track and a Ch16 reference architecture, and write a task spec scoped to *a version of* it that keeps the seam. Point the shipped Module 7 governed fleet at your spec through `run_exam.py` — it imports the real fleet via `fleet_adapter.py`, never a rebuild — and operate the console: work the HITL inbox to approve the merge by id, read the four-clause audit, hold the kill switch, stay under the team budget. Then run `rubric.py` to grade the produced run against the seven acceptance criteria. Start by running `python smoke.py` to watch the fleet ship the sample system and the rubric grade it, then `python -m pytest tests/` for the offline gate.

</div>
