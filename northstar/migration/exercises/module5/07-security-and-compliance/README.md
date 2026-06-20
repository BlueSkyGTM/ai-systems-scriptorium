# Exercise 07 — Security & Compliance for AI Ops

## Goal

Add a security layer to `module5-serving/`: resolve the provider key from a vault at startup instead of holding it in code, and gate every request on an `(identity, role, tenant)` check so a caller can only reach routes its role permits and only touch its own tenant's data. Prove a hardcoded or missing secret fails startup loudly, and that cross-tenant access is denied.

## Why

The serving stack from the earlier lessons holds a provider key and answers requests across tenants. A key in a config file is a key already half-leaked, and a serving layer that doesn't check the tenant on every request is one cache hit away from leaking customer A's data into customer B's answer. This exercise adds the two infrastructure-layer controls that make the platform auditable: secrets resolved at runtime (never stored), and least-privilege access enforced at the request boundary. It is the infra-layer counterpart to the Module 3 MCP tool scoping and the Module 4 guardrails — same discipline, one layer down.

## Steps

1. **Secrets from a vault.** Add `module5-serving/security/secrets.py` with `load_provider_key(env: dict) -> str`. Simulate the vault with environment variables — read the key from a `VAULT_PROVIDER_KEY` entry, not from any source file. Raise a clear error at startup if the key is absent. Add a startup check that scans the serving config/source for an inline key pattern (e.g., a string matching `sk-...`) and refuses to boot if one is found — the codebase must contain no literal key.

2. **Identity on the request.** Give each incoming request a signed identity header carrying `user_id`, `role`, and `tenant_id` (a plain HMAC over the fields with a shared test secret is enough — no real auth provider). Add `verify_identity(headers, secret) -> Identity | None` that returns the parsed identity on a valid signature and `None` on a bad or missing one. A request with no valid identity is rejected before any model call.

3. **RBAC check.** Define a route→roles map (e.g., `"/admin/rollback"` needs `operator`, `"/infer"` needs `user` or `operator`, `"/costs"` needs `analyst`). Add `authorize(identity, route) -> bool`. Reject with an `[access denied: role <role> may not reach <route>]` observation when the role lacks the route. Confirm the admin/operator role cannot, by default, read the secret-loading path — separate the duty.

4. **Tenant isolation.** Every request names the resource it wants (a `tenant_id` on the data it reads). Add a check that rejects any request whose identity `tenant_id` doesn't match the resource `tenant_id`, with a `[tenant mismatch]` observation. Enforce it on the retrieval path *and* on a simulated cache lookup — show that a cache key without the tenant would leak, and that keying the cache by `(tenant_id, query)` closes it.

5. **Run the proof sequence.** Boot once with no `VAULT_PROVIDER_KEY` (startup fails loudly). Boot once with an inline key planted in the source (startup refuses). Boot clean. Then: a valid `user` hits `/infer` (allowed); a `user` hits `/admin/rollback` (role denied); tenant A requests tenant B's document (tenant denied); tenant A requests its own document (allowed); the same query for tenant A and tenant B returns from cache without crossing over.

## Done when

- Startup fails with a clear error when the provider key is missing, and refuses to boot when a literal key is found in the source.
- The provider key is read only from the simulated vault at runtime — no key string exists anywhere in the codebase.
- A request with no valid signed identity is rejected before any model call.
- A role without a route is denied; a tenant requesting another tenant's resource is denied; both with distinct observations.
- The cache is keyed by tenant, and a cross-tenant cache hit is shown to be impossible.

## Stretch

Add an append-only audit log: every privileged action (a denied access, a key load, a rollback) writes a structured line with timestamp, identity, action, and outcome — and confirm the log is append-only (a write never mutates a prior line). Then sketch a single "policy gate" function that runs before deploy and refuses a config that sets a disallowed region or skips encryption — the local stand-in for an Azure Policy `deny` effect, proving compliance can be a pipeline gate rather than a manual review.
