# Safe Rollout: Shadow, Canary, A/B + AI Gateways

Swapping a model in production is the most dangerous deploy you will ever do, because the thing you changed has no unit test that fails when it gets worse. A new model version compiles, serves, and returns plausible text — and quietly degrades on the cases that matter, with the complaint arriving weeks later. Progressive delivery is how you let a fraction of traffic find the regression before all of it does.

## Why a Model Rollout Is the Hard Case

A normal deploy has a binary failure: the build breaks, a test goes red, the error rate spikes, you roll back. A model rollout has none of those guarantees. The failure modes are diffuse — a subtle drop in faithfulness, a creeping increase in refusals, an output that got longer and three times more expensive — and the signal is delayed, because "is this answer good?" is not something a 200 status code can tell you.

Worse, the output is not even stable run to run. Identical inputs can produce measurably different results across runs, because floating-point arithmetic is non-associative and the GPU kernels are not batch-invariant — the reduction order shifts with the batch size, which shifts with concurrent load — so "the same" means *within variance*, not *identical*. You cannot diff two responses and call a difference a bug. You have to roll out in stages, measure distributions, and keep the escape hatch one flag away.

## Three Stages, Each Catching What the Last Cannot

The progression is shadow, then canary, then A/B — not a menu, a sequence. Each stage answers a question the previous one could not.

**Shadow mode** sends a copy of live production traffic to the candidate model and throws the response away. Users never see it; you log what the candidate *would* have said and diff it against production. Shadow is your zero-risk catch for the operational regressions: a cost blow-up, a latency cliff, an output-length explosion. What it cannot catch is quality — nobody is reading the shadow responses, so a candidate that is cheaper, faster, and subtly dumber sails through. Shadow proves the candidate is *safe to serve*, not that it is *good*.

**Canary** is the first stage where real users touch the candidate. You route a sliver of traffic to it — 1%, then 10%, 25%, 50%, and up — and gate each promotion on a fixed set of metrics: latency percentiles, cost per request, error and refusal rate, output-length distribution, and whatever user-feedback signal you have. If any metric crosses its threshold at one step, promotion halts and traffic reverts. The percentages are deliberately small at the start because the blast radius is the point: a bad canary burns 1% of traffic for a few minutes, not all of it for a day.

**A/B testing** answers a different question than either. Shadow and canary ask *is the candidate safe to ship?* — an operational question about regressions. A/B asks *do users prefer A or B?* — a product question about two genuine alternatives. It needs randomized user-level assignment and a metric you actually care about (task completion, retention, thumbs-up), and you run it when you have two real options to choose between, not every time you ship. Evals tell you whether the model *can* do the job; the A/B test tells you whether users *care*. Both are required, and shipping on a hunch is over.

This is exactly the eval thread's outer loop. Module 2 built the inner loop — LLM-as-judge scoring outputs against a rubric at development time, before code reached staging. Those same judges run here, but now against live canary traffic instead of a fixed test set: the judge that gated your prompt in CI becomes the quality gate that decides whether the canary advances. Same discipline, production scale. The inner loop hands off to the outer loop, and this is where the handoff happens.

## The Gateway Is Where Rollout Becomes a Config Change

None of this works if shipping a new model means a redeploy. The mechanism that makes rollout fast is an **AI gateway** — a service that sits between your apps and the model backends, exposing one stable API while it decides, per request, which backend serves it. Routing weights live in the gateway's config. Moving a canary from 10% to 25%, or slamming it back to 0% when a metric trips, is a config flip measured in seconds, not a deploy measured in hours.

The gateway earns its place beyond rollout. It consolidates provider routing, fallback when a backend returns a 429, retries, per-consumer rate limits, secret references pulled from a vault at runtime, and cost attribution — one OpenAI-compatible surface in front of many models. On Azure, this is Azure API Management acting as the AI gateway: it provides built-in backend pools, load balancing, and circuit breaking across multiple Azure OpenAI deployments, so a throttled or faulted backend drops out of the pool and traffic reroutes without the client knowing. Its smart load balancer reacts to the 429 "too many requests" signal specifically, reading the `Retry-After` header the backend returns and routing around the throttled deployment to a healthy one by priority rather than blind round-robin. And it enforces a tokens-per-minute limit and a token quota per consumer with the `llm-token-limit` policy, so one app's rollout cannot starve another of capacity.

Rollback is the weapon the whole structure exists to keep loaded. Keep the *policy* — which model is live, at what weight — in the gateway's flags, and keep the *model* in a registry pinned to an exact digest. A bad rollout is then a flag flip plus a revert to a pinned version, done in seconds. The non-determinism means you can never promise a rollout is identical to what came before; the registry and the flags mean you can always make it *reversible*, which is the property that lets you ship at all.

## Core Concepts

- A model rollout is the hard deploy: no failing test, diffuse and delayed failure modes, and output that varies run to run from GPU non-determinism — so "stable" means within variance, and you roll out in stages with rollback one flag away.
- Shadow → canary → A/B is a sequence, not a menu: shadow catches operational regressions (cost, latency, length) at zero user risk but never quality; canary exposes a metric-gated traffic sliver to real users; A/B answers the product question of which of two alternatives users prefer.
- Canary gating is the eval thread's outer loop — the Module 2 LLM-as-judge that gated prompts in CI now scores live canary traffic to decide promotion; evals ask whether the model can do the job, A/B asks whether users care, and both are required.
- An AI gateway turns rollout into a config change: one stable API in front of many backends, with routing weights, fallback, rate limits, and secrets centralized — so promoting or reverting a canary is a seconds-long flag flip, backed by a registry of digest-pinned models.

<div class="claude-handoff" data-exercise="exercises/module5/05-safe-rollout/">

**Build It in Claude Code** — Add a shadow/canary router to `module5-serving/` that fronts two model backends behind one endpoint: in shadow mode it mirrors every request to the candidate and logs a diff without affecting the response, and in canary mode it splits traffic by a configurable weight and reverts to 0% when a gated metric (cost, latency p99, or refusal rate) crosses a threshold. Prove the flip and the auto-revert happen as config changes, with no restart.

</div>
