# VERIFY verdict — M5 L07 · Security & Compliance for AI Ops

**Verifier:** Sonnet VERIFY subagent · **Date:** 2026-06-19
**Draft:** `build-stages/m5/output/author/07-security-and-compliance.md` (edited in place)
**Verdict:** **PASS** (markers resolved, claims sourced, compliance discipline held)

---

## Claim ledger

| # | Claim | Authority | Result |
|---|-------|-----------|--------|
| 1 | Secrets never in VCS / env files / images; live in a vault (Vault / AWS Secrets Manager / Azure Key Vault); process fetches at runtime; rotate ≤90 days; scan commits (Gitleaks/TruffleHog) | aefs Ph17 L25 | **CONFIRMED** — L25 states exactly this: centralize secrets, never config/env/static, ≤90-day rotation, TruffleHog/GitGuardian/Gitleaks on every commit. |
| 2 | 2026 supply-chain attacks read env vars off compromised CI pipelines | aefs Ph17 L25 | **CONFIRMED (softened)** — source names the specific "Vercel supply-chain attack" exfiltrating env vars across thousands of deployments via compromised CI/CD credentials. Draft generalizes to "the 2026 supply-chain attacks" — defensible, no unverifiable specific. |
| 3 | Passwordless pattern: managed identity + `Key Vault Secrets User` role; app references secret by URI; versionless URI auto-flows rotated secret; `DefaultAzureCredential` picks up managed identity in prod / az-login locally | MS Learn (connector) | **CONFIRMED** — `app-service/app-service-key-vault-references`, `entra/.../managed-identities-azure-resources/overview`, `key-vault/general/rbac-guide`, `key-vault/secrets/quick-create-net`. `Key Vault Secrets User` is the correct RBAC data-plane role; versionless URI = automatic latest-version pickup; `DefaultAzureCredential` is the documented dual-path pattern. Code snippet is accurate. |
| 4 | Least privilege at two layers: RBAC/ABAC (who operates) + tenant isolation (who reads whose data); enforce tenant key at vector store, cache, prompt builder; admin should not read secrets | aefs Ph17 L25 + asdg Ch12 §02 | **CONFIRMED** — asdg Ch12 §02: RBAC, ABAC, tenant isolation at vector DB / cache / prompt-building levels; cross-tenant context pollution named explicitly. Separation-of-duties (admin ≠ secret reader) confirmed by MS Learn `secure-key-vault` (app contributors can have full App Service control yet no Key Vault data access). |
| 5 | Egress whitelisting: inference pods in dedicated subnet allowing only provider endpoints + vault | aefs Ph17 L25 | **CONFIRMED** — L25: "LLM pods in a dedicated subnet whitelisting only `api.openai.com` / `api.anthropic.com`." |
| 6 | Redaction before the model: PII/PHI detected+masked at inference boundary (Presidio); post-hoc cleanup is theater | aefs Ph17 L25 + asdg Ch13 §01 | **CONFIRMED** — L25 (spaCy NER / Presidio), asdg Ch13 (PII detection/redaction), aefs L26 (real-time inference-layer redaction is the defensible standard; post-processing means the model already saw the data). |
| 7 | Append-only audit log of every privileged action | asdg Ch12 §02 | **CONFIRMED** — "comprehensive audit logging for compliance reporting." |
| 8 | SOC 2 Type II (not Type I) is the enterprise/fintech procurement gate; Type II = controls operated effectively over months; what it makes you build: access reviews, audit logging, change management, evidence | WebSearch (a-lign, Secureframe, KirkpatrickPrice) + aefs L26 | **CONFIRMED** — Type II attests operating effectiveness over a period (6-mo minimum, commonly 3–12 mo); Type I is point-in-time design only. aefs L26: "SOC 2 Type II (not Type I) is the fintech gate." |
| 9 | HIPAA: no PHI leaves infra until a signed BAA is in place with every party that touches it, provider included | WebSearch (HIPAA Journal, NordLayer, Censinet) + aefs L26 | **CONFIRMED** — BAA required before any vendor creates/receives/maintains/transmits PHI; provider included. aefs L26: "HIPAA requires a signed BAA before any PHI leaves infra." |
| 10 | EU AI Act: applies if you serve EU users regardless of where you sit; high-risk obligations carry enforcement + fines "large enough to notice"; build = logging/traceability, human oversight, risk docs, transparency | WebSearch (William Fry, Lexology, Modulos) + aefs L26 | **CONFIRMED** — extraterritorial (mirrors GDPR): applies to non-EU providers placing systems on EU market / whose output affects EU users. High-risk obligations + fine regime exist. Draft deliberately omits the deadline (Aug 2 2026) and fine percentages (€35M/7%, €15M/3%) that aefs L26 carries — **correct compliance discipline.** |
| 11 | Azure Policy: `deny` effect blocks a violating resource at creation; `audit` flags without breaking deploys; stage as audit-only before deny; compliance becomes a pipeline gate | MS Learn (connector) | **CONFIRMED** — `governance/policy/concepts/effects` + `effect-basics`: deny blocks creation/update of non-compliant resources, audit marks non-compliant without breaking (default effect), staging audit→deny is the documented pattern. |

## Markers resolved (5 / 5)

All bracketed markers removed → clean prose. No URLs left inline (lesson voice carries no inline citations; URLs captured in this ledger).
- L13 `[MS-Learn: Key Vault references / managed identity]` → removed (claim #3 confirmed)
- L47 `[verify: SOC 2 Type II gate / Type I vs II]` → removed (claim #8 confirmed)
- L49 `[verify: HIPAA BAA before PHI]` → removed (claim #9 confirmed)
- L51 `[verify: EU AI Act scope / obligations / timeline]` → removed (claim #10 confirmed; the editorial "don't state deadlines/fines from memory" sentence retained as voice)
- L53 `[MS-Learn: Azure Policy effects]` → removed (claim #11 confirmed)

## Compliance-specifics check (CRITICAL)

**PASS.** Full grep for dates / fine thresholds / statutory citations (`20\d\d|€|%|Article|Art.|§|CFR|deadline|fine|GDPR`) returns only: (a) "2026 supply-chain attacks" — a softened generalization, no statutory content; (b) the EU AI Act paragraph, which carries NO specific date, fine percentage, or article number and explicitly instructs the reader not to cite them from memory. No unverifiable compliance specific ships.

## M4 cross-ref

N/A for this lesson directly (the M4 budget cross-ref lives in L08). L07's continuity claim — "Module 3 verified at the tool boundary, Module 4 verified at the action boundary, this lesson verifies at the infrastructure boundary" — is an accurate thread restatement consistent with PLAN's security through-line.

## STYLE pass

One H1; seam lead grabs (problem + why the platform engineer owns it); one `## Core concepts` (4 props, stated as claims); handoff div present and well-scoped; no template ending (ends on a reframe — "a diagram, not a promise"); acronyms expanded on first use (SOC 2, HIPAA, EU AI Act, RBAC, ABAC, PII/PHI, BAA, Entra ID); second person / present tense / active voice held throughout. No defects.

## Defects fixed

None beyond marker removal. Prose was clean and accurate as drafted.

## FLAGGED

None blocking. (Minor: the Azure Key Vault default-RBAC change to API version 2026-02-01 and Foundry RBAC role renames are live but not referenced by this lesson — no action.)
