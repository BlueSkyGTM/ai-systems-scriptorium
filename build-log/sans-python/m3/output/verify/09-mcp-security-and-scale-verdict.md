# Verdict: 09-mcp-security-and-scale

## Markers resolved

6 MS-Learn markers → all RESOLVED.

1. `[MS-Learn: Azure API Management — enforcing content policy on MCP tool descriptions and auditing tool registration events]`
   - **URLs:** https://learn.microsoft.com/azure/api-management/mcp-server-overview, https://learn.microsoft.com/azure/foundry/agents/how-to/tools/governance
   - **Grounded fact:** Azure API Management applies policies (auth, rate limiting, IP filtering, audit logging) at the MCP server layer — the same control point where description-integrity enforcement belongs.

2. `[MS-Learn: Azure AI Foundry — implementing role-based access control for MCP tool capabilities and approval workflows]`
   - **URL:** https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol
   - **Grounded fact:** Foundry Agent Service's `require_approval` field (`always`/`never`/named allowlist) implements per-tool approval scoping. Azure RBAC on the Foundry resource controls who can configure those gates.

3. `[MS-Learn: Azure Entra ID — configuring OAuth 2.1 with PKCE for MCP server authentication and audience-pinned token validation]`
   - **URLs:** https://learn.microsoft.com/azure/api-management/secure-mcp-servers, https://learn.microsoft.com/entra/identity-platform/claims-validation
   - **Grounded fact:** Microsoft Entra ID is the identity provider; `validate-azure-ad-token` policy in Azure API Management enforces audience (`aud`) claim checking. PKCE confirmed via the MCP APIM sample (`PKCE-enabled public client` in Azure Samples). OAuth 2.1 / `/.well-known/oauth-authorization-server` confirmed in APIM MCP OAuth spec implementation.

4. `[MS-Learn: Azure API Management — enforcing OAuth 2.1 Bearer token validation on MCP Streamable HTTP endpoints]`
   - **URL:** https://learn.microsoft.com/azure/api-management/secure-mcp-servers
   - **Grounded fact:** APIM supports both subscription-key and OAuth 2.1 Bearer token auth on MCP Streamable HTTP endpoints via inbound policies. Confirmed from the secure-mcp-servers documentation.

5. `[MS-Learn: Azure API Center — registering and discovering MCP servers as managed APIs with centralized governance]`
   - **URL:** https://learn.microsoft.com/azure/api-center/register-discover-mcp-server
   - **Grounded fact:** Azure API Center is the registry layer — register as managed assets, discovery portal with test console, auto-sync from API Management.

6. `[MS-Learn: Azure API Management — building an MCP gateway with rate limiting, RBAC, and audit logging for multi-server deployments]`
   - **URL:** https://learn.microsoft.com/azure/api-management/mcp-server-overview
   - **Grounded fact:** Azure API Management exposes multiple MCP servers through one managed endpoint with declarative policies for rate limiting, JWT validation, IP filtering, and Azure Monitor forwarding. Confirmed from APIM MCP overview documentation.

## Ending rewrite

**Old (banned template):**
> An AI Platform Engineer who ships this stack has moved from "I trust everything in my process" to "I verify everything at the boundary" — and that shift is what separates a prototype from a production agent system.

**New:**
> Prototypes trust everything in the process. Production systems verify at every boundary. That gap is exactly what this chapter's four lessons close — one layer at a time.

Shape: contrast (prototype vs. production) + resolution. The "one layer at a time" close ties back to the security thread section immediately above it, giving the reader a backward glance that feels earned. No template opener.

## Preserved per task spec

- MCP `2025-11-25` spec revision reference: kept (lesson 09, OAuth 2.1 section).
- OAuth 2.1/PKCE: kept and grounded.
- SEP-1686/SEP-1724 references in lesson 08: kept (per task C instruction).
- Python `pkce_pair()` snippet: preserved verbatim.
- TypeScript `MUTATION_ALLOWLIST` snippet: preserved verbatim.
- Gateway diagram (ASCII): preserved verbatim.

## STYLE conformance

- §4 ending: banned template removed. New ending is a contrast/resolution shape. PASS.
- §8 variety: lesson is long but rhythmically varied — short declarative attacks, longer clause-chain explanations, one "defense" bulleted list (tool poisoning section). The "that shift" phrasing in the old ending was the only true robotic tell; removed. PASS.
- §1 unity: second person throughout ("you," "your"). Present tense. PASS.
- Code: TypeScript and Python snippets preserved. Gateway diagram preserved. PASS.

## VERDICT: PASS
