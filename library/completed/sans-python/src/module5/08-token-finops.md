# Token FinOps & cost optimization

The first time finance asks why the AI bill tripled last month, you will discover whether you can answer. If the only number you have is the provider's total invoice, you can't — you can't say which feature, which customer, or which bad prompt drove it, so you can't cut it without cutting blind. FinOps — financial operations, the practice of treating cloud spend as an engineering metric — starts the moment you decide the bill is a number you own, not a surprise you receive.

Module 4 already gave you the governor: a per-task budget that caps one agent's spend, trips a kill switch on breach, and routes cheap steps to a cheap model. That defends one wallet. This lesson is the other altitude — the *platform* bill, summed across every agent, every user, every tenant, every team. Same instinct, different unit of accounting. The governor stops a runaway; FinOps tells you where all the money goes when nothing is running away, and gives you the levers to make the steady-state bill smaller without making the product worse.

## The bill is a first-class metric

Traditional cloud FinOps breaks on LLM spend, and it breaks for a specific reason. Old-world cost is resource-uptime — a VM costs the same whether it's busy or idle, and a tag on the VM follows the bill. LLM cost is token-transactions: it scales with what each request *does*, and the provider invoice arrives as one undifferentiated number with no tags attached. Worse, the cost drivers are engineering decisions. Prompt length, context-window size, output length, how many tool calls a loop makes — every one of those is a line on the bill, set by code, invisible to a VM-shaped cost tool.

So you instrument attribution at the call site, and you do it on day one, because retroactive tagging always misses the spend that already happened. Stamp three dimensions on every model call: `user_id` (who), `task_id` plus the route (what), and `tenant_id` (whose budget). Those three turn one opaque invoice into a query — cost per customer, cost per feature, cost of the route that quietly got expensive. Track the token *layers* too, because one bucket hides the problem: prompt tokens, tool-call tokens, memory/context tokens, and response tokens land in different proportions, and the one that surprises you is usually the context you forgot you were re-sending every turn.

The unit metric is the lever that makes the whole thing legible: not dollars per million tokens, which means nothing to anyone outside the platform team, but **cost per resolved query** or **cost per artifact** — the spend to produce one unit of business value. That number you can put next to revenue, and that number tells you whether an optimization helped or only shuffled tokens around.

```python
# module5-serving/finops/attribution.py — stamp every call, sum any way you ask
from dataclasses import dataclass

# Simulated rate card ($/1M tokens). Real numbers live in config and shift — verify.
RATES = {"big": {"in": 3.00, "out": 15.00}, "small": {"in": 0.25, "out": 1.25}}

@dataclass
class Charge:
    user_id: str
    tenant_id: str
    task_id: str
    route: str          # which model tier served it
    in_tok: int
    out_tok: int

    def usd(self) -> float:
        r = RATES[self.route]
        return self.in_tok / 1e6 * r["in"] + self.out_tok / 1e6 * r["out"]
```

On Azure this attribution exists at the platform layer too. Cost Management groups spend by tag through tag inheritance and cost-allocation rules, and Microsoft Foundry stamps every project with a `project` tag automatically, so you filter the cost-analysis view by project to split a shared deployment's bill across teams for showback or chargeback. The call-site stamping above is the same idea pushed down to per-request granularity — finer than the invoice can reach on its own.

## The levers that cut the bill

Once you can see the spend, four levers move it — in rough order of effort-to-payoff.

**Caching is the cheapest large win.** Two layers, and they compound. Provider prompt caching reuses the model's attention state for a stable prefix: mark the system prompt and tool schemas as cacheable and you stop paying full freight to re-send them every turn — cached reads run a fraction of fresh-input price. Application-level semantic caching goes further and skips the model entirely: hash the request, and if a near-identical one was answered recently, return the stored answer for zero tokens. Hit rates run wide — single digits on open-ended chat, far higher on structured, repetitive traffic like FAQ. Two traps collapse the savings: dynamic content in the prefix (a timestamp or request ID poisons the cache key and drives hits to zero), and parallel cold requests that all miss before the first write lands, so you pay N writes and zero reads. Order the prompt so the stable part comes first; that ordering *is* the cache key.

**Tiered routing is cost governance applied to the model choice** — the same routing you met in the budget governor, now a fleet-wide policy instead of a per-task tactic. A broker reads each request and sends the easy, high-volume work (classification, extraction, a rubric score) to a small fast model, escalating only the genuinely hard requests to the frontier model. Production teams report meaningful cost reduction at equal quality, because routing everything to the top model is the most common way a team triples its bill for no accuracy gain. The risk is cheap-model drift: the route quietly pushes too much to the weaker model, quality slips a few points, and nobody notices for a quarter — so gate the route on an online quality signal, not on an offline eval alone.

**Batch is the discount you're probably leaving on the table.** Every major provider offers an async batch tier at roughly half price with a turnaround measured in hours. The rule is blunt: if it isn't interactive, it belongs on batch. Triage every workload into three lanes — interactive (synchronous, cached), semi-interactive (queued with a fallback), and batch (overnight). Stack the batch discount on top of prompt caching and an overnight pipeline's cost drops toward a tenth of running it synchronously and uncached.

**Quotas and rate limits are the backstop that bounds the worst case.** This is where FinOps meets the multi-tenant boundary: a tenant whose traffic spikes — organically or maliciously — can't be allowed to consume the whole platform's capacity or budget. Azure OpenAI enforces this natively. Quota is allocated in **Tokens-Per-Minute (TPM)** per deployment, with a proportional Requests-Per-Minute limit; exceed it and the API returns a `429` with a `retry-after-ms` header telling the client how long to wait. Watch the `x-ratelimit-remaining-tokens` response header to throttle *before* you hit the wall instead of after. The platform pattern layers three caps: a per-tenant rate limit set a few multiples above peak, a daily spend cap above that, and a hard kill switch when spend jumps past a statistical threshold — the same fail-closed escalation the Module 4 governor applied to one task, now applied to a tenant.

## Tie it back, then forward

The continuity with Module 4 is the point, not a coincidence. The budget governor is the per-agent floor: deterministic code that caps one task and trips a switch on breach. FinOps is the same discipline read at platform scale — attribution instead of one ledger, fleet-wide routing policy instead of one route decision, tenant quotas instead of one velocity limit. You don't rebuild the governor here; you sum it. Define the cap once at the task, attribute the spend everywhere, and the platform bill becomes a thing you steer instead of a thing that happens to you.

The optimizations aren't free, and that is the discipline's last rule: every lever trades something. Caching trades freshness, routing trades a quality floor you have to monitor, batch trades latency, quotas trade headroom under a real spike. The instrumentation is what tells you whether the trade paid — which is why attribution comes first and the levers come second. Measure, then cut; an optimization you can't attribute is a guess you'll pay for twice. Answer "why did the bill triple?" in a single query and the decision about it is yours to make — answer it with a shrug and someone above you makes that call instead.

## Core concepts

- LLM cost is token-transactions, not resource-uptime, and the provider invoice arrives untagged — so you instrument attribution at the call site on day one (`user_id`, `task_id`+route, `tenant_id`) and report cost per resolved query, because retroactive tagging always misses the spend that already happened.
- Four levers cut the bill: caching (provider-prefix + semantic, ruined by dynamic prefixes and parallel cold misses), tiered routing (cheap model for easy work, gated on an online quality signal to catch drift), batch (~half price for anything non-interactive), and quotas/rate limits (per-tenant TPM caps with 429/retry-after as the multi-tenant backstop).
- FinOps is Module 4's budget governor read at platform scale: the governor caps one task and trips a switch; FinOps attributes spend fleet-wide, routes as policy, and quotas per tenant — sum the governor, don't rebuild it.
- Every optimization trades something — freshness, a quality floor, latency, headroom — so attribution comes before the levers: measure, then cut, because an optimization you can't attribute is a guess you pay for twice.

<div class="claude-handoff" data-exercise="exercises/module5/08-token-finops/">

**Build It in Claude Code** — add a FinOps layer to `module5-serving/`: a cost-attribution middleware that stamps every simulated request with `user_id`, `tenant_id`, `task_id`, and route, computes a simulated token cost from a rate card, and emits a per-dimension cost report. Then add two levers and prove they cut the bill: a semantic cache that returns a stored answer for repeated requests at zero token cost, and a tiered router that sends easy requests to a cheap model and hard ones to the expensive model. Run a fixed workload three ways — no optimization, caching on, caching plus routing — and show the total cost dropping each time, with the attribution report proving *where* it dropped. Reuse the Module 4 `TaskBudget` as the per-task cap underneath; do not rebuild it. Local only — no real provider, simulated costs throughout.

</div>
