# Security & Compliance for AI Ops

Your serving stack holds an API key worth thousands of dollars a day and answers questions about other people's data. The application layer can be flawless and you still lose the company if that key sits in a config file or the wrong tenant reads the wrong context. Security here is not the model's behavior — it is the substrate the model runs on, and it is the platform engineer's name on the incident report.

You have hardened the layers above this one. Module 3 scoped MCP tools, pinned descriptions, and put OAuth on remote servers. Module 4 wrapped the agent in guardrails and a kill switch. Those defend what the model *does*. This lesson defends where it *lives* — the secrets it reaches for, the identities that can touch it, the surface an attacker probes — and it folds the compliance frameworks in as engineering requirements, not legal reading. SOC 2 (a security-controls audit), HIPAA (US health-data law), and the EU AI Act don't ask you to feel responsible. They ask you to build specific things. Build them.

## Secrets never live in the code

The provider key is the crown jewel, and the most common way to lose it is the most boring: someone commits it. Not in the app — in a config file, a `.env` checked in by accident, a notebook, a CI log. The 2026 supply-chain attacks didn't crack encryption; they read environment variables off compromised build pipelines. A static key in a file is a key already half-leaked.

The rule is absolute: no credential in version control, no credential in an environment file, no credential baked into an image. The credential lives in a vault — HashiCorp Vault, AWS Secrets Manager, Azure Key Vault — and the running process fetches it at startup or pulls it through the gateway at request time. Rotate on a fixed schedule (a 90-day ceiling is the defensible standard) and scan every commit with a tool like Gitleaks or TruffleHog so a leaked key fails the build instead of reaching production.

The pattern that makes rotation painless is *passwordless*: the process never holds a long-lived key at all. On Azure, you give the serving workload a **managed identity** — an identity Microsoft Entra ID manages for it — and grant that identity the `Key Vault Secrets User` role on the vault. The app references the secret by URI; the platform resolves it at runtime against the identity. No key in code, no key in app settings, and rotation propagates with no redeploy because the app holds a *reference*, not a value. Use the versionless secret URI so a rotated secret flows through automatically.

```python
# module5-serving/security/secrets.py — resolve at startup, never store
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def load_provider_key(vault_url: str) -> str:
    # DefaultAzureCredential picks up the workload's managed identity in prod,
    # the developer's az-login session locally. No secret in either path.
    client = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())
    return client.get_secret("provider-api-key").value
```

## Least privilege is the whole access model

A serving platform is multi-tenant by default — many users, many teams, sometimes many customers, all behind one set of model deployments. Least privilege means each identity reaches exactly what it needs and nothing more, and it applies at two layers that people conflate.

**Who can operate the platform.** Role-based access control (RBAC) maps an identity to a role to a permission: the on-call engineer can roll back a deployment, the analyst can read the cost dashboard, neither can read the vault. Attribute-based access control (ABAC) adds conditions on top — this role, but only on resources tagged for this team. The discipline is the same one Module 3 applied to MCP tools, now applied to the infrastructure: the human who administers the platform should not, by default, be able to read the secrets the platform uses. Separate the duties.

**Who can read whose data.** This is the tenant-isolation boundary, and it is the one that ends careers when it leaks. Cross-tenant context pollution — tenant A's documents surfacing in tenant B's RAG answer — is the AI-native version of a data breach, and it hides in three places: the vector store (filter retrieval by `tenant_id`, always), the cache (a cache key without the tenant is a cross-tenant leak waiting for a cache hit), and the prompt builder (never assemble one tenant's context into another's request). Enforce the tenant key at every layer, because the layer you skip is the one that leaks.

## The deployment attack surface

An attacker who can't break the model attacks everything around it. Map the surface and close it.

The egress path is the exfiltration path. If a compromised serving pod can reach the open internet, a successful prompt injection can phone home with whatever it scraped. Put inference workloads in a dedicated subnet that whitelists only the provider endpoints they legitimately call — `api.openai.com`, `api.anthropic.com`, your vault — and denies the rest. A pod that can only talk to three hosts can leak to only three hosts.

The data path needs a redaction stage *before* the model sees a request, not after it answers. Personally identifiable and health information (PII and PHI) gets detected and masked at the inference boundary with an entity recognizer like Presidio; post-hoc cleanup is theater, because by then the model already processed the raw data and it already sits in your logs and your provider's. And every privileged action — a key rotation, a deployment, a config change — writes to an append-only audit log, because an attack you can't reconstruct is an attack you can't prove you contained.

## Compliance is a build spec

The frameworks read like legal documents and land as engineering tickets. Translate them:

**SOC 2** asks: can you prove your controls work over time? The Type II report (the one that matters; Type I is a single snapshot) is the audit that fintech and enterprise buyers gate deals on. What it makes you build: access reviews, audit logging, change management, and evidence that the controls ran for months — which is exactly the RBAC and audit-log work above, plus the discipline to keep the evidence.

**HIPAA** governs US health data and has one non-negotiable trigger: no protected health information leaves your infrastructure until a Business Associate Agreement (a BAA — the signed contract making the provider liable for the data) is in place with every party that touches it, your model provider included. No BAA, no PHI. What it makes you build: the PII/PHI redaction stage, encryption in transit and at rest, and the audit trail proving who accessed what.

**The EU AI Act** is the one that changed the calculus, because it applies to you if you serve EU users regardless of where you sit, and its high-risk obligations carry enforcement and fines large enough to notice. What it makes you build: logging and traceability of model decisions, human oversight on high-risk use, risk documentation, and transparency about what the system is. It is, in engineering terms, an observability-and-governance mandate — the traces and decision logs you build in the observability lesson are the same artifacts an EU AI Act audit asks for. Don't state the deadlines or the fine percentages from memory; they shift, and a wrong number in front of an auditor is worse than no number.

The platform move is to stop treating these as a year-end scramble and encode them as policy that fails closed. Azure Policy is the mechanism: a policy definition with a `deny` effect blocks any resource that violates a rule at creation time — a storage account without encryption, a deployment in a disallowed region — while an `audit` effect flags noncompliance without breaking deploys, so you stage a control as audit-only before you turn it to deny. Compliance becomes a gate in the pipeline, not a binder someone updates after the fact.

The through-line across this chapter is the through-line of the whole guide's security thread: prototypes trust the environment, production verifies at every boundary. Module 3 verified at the tool boundary, Module 4 verified at the action boundary, and this lesson verifies at the infrastructure boundary — the secret, the identity, the tenant, the egress. Each control is thin on its own. Stacked, they make the platform something an auditor can sign and an attacker can't quietly walk through. The day a regulator or a customer's security team asks how you handle their data, the answer is a diagram, not a promise.

## Core concepts

- Secrets never live in code, env files, or images — they live in a vault and the workload fetches them at runtime through a managed identity, so rotation propagates with no redeploy and a leaked static key can't exist to begin with.
- Least privilege runs at two layers: RBAC/ABAC controls who can operate the platform (and the admin should not be able to read the secrets), and tenant isolation controls who reads whose data — enforced at the vector store, the cache, and the prompt builder, because the layer you skip is the one that leaks.
- The deployment attack surface is closed by egress whitelisting (a pod that reaches three hosts leaks to three hosts), redaction before the model sees PII/PHI, and an append-only audit log of every privileged action.
- SOC 2, HIPAA, and the EU AI Act are build specs, not legal theory: they make you build audit logging, access reviews, BAAs, redaction, and decision traceability — encode them as fail-closed policy (Azure Policy `deny`/`audit`) so compliance is a pipeline gate, not a year-end scramble.

<div class="claude-handoff" data-exercise="exercises/module5/07-security-and-compliance/">

**Build it in Claude Code** — add a security layer to `module5-serving/`: a `secrets.py` that resolves the provider key from an environment-backed "vault" at startup and refuses to run if the key is hardcoded or missing, and an access-check middleware that gates every request on an `(identity, role, tenant)` tuple — rejecting a caller whose role lacks the route and rejecting any request whose `tenant_id` doesn't match the resource it asks for. Prove cross-tenant access is denied and that a missing-secret startup fails loudly. Local only — no cloud, no real vault; simulate the vault with environment variables and the identity with a signed header. Open the repo and run the exercise for this lesson.

</div>
