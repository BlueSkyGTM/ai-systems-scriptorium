# Exercise 09 — MCP Security and Scale

## Goal

Harden the MCP server from lesson 08 with a description linter, SHA-256 hash pinning, a mutation allowlist with an approval hook, and a client-side OAuth 2.1 PKCE sketch.

## Why

An MCP server that trusts its own tool descriptions and allows all mutations is a prototype, not a production system. This exercise adds the defenses that make the server auditable, the mutation surface explicit, and the auth posture correct before a remote deployment.

## Steps

1. **Description linter.** Add `module3-agent/mcp-server/security/linter.ts`. Implement `lintDescriptions(tools: ToolDefinition[]): LintResult[]` — flag any description that contains injection-pattern phrases (e.g., "ignore previous", "system prompt", "exfiltrate", "do not tell", plus a configurable list). Run this function at server startup; throw if any tool fails. Add a test tool with a poisoned description and confirm the server refuses to start.

2. **Hash pinning.** Add `module3-agent/mcp-server/security/pinner.ts`. On first `tools/list` call, SHA-256 hash every tool description and store the pins in a `Map<toolName, hash>`. On every subsequent `tools/list` response — from any server, including backends the gateway might proxy — recompute and compare. If a description changed, log `[security] rug pull detected: <name>` and terminate the session. Verify: register a tool, save its pin, mutate its description in memory, call `tools/list` again, confirm the session terminates.

3. **Mutation allowlist.** Add `MUTATION_ALLOWLIST: Set<string>` to the server config. Update the tool execution path: if `isMutating(toolName)` and the tool is not in the allowlist, return `[error] tool not on mutation allowlist: <name>`. If it is in the allowlist, call the approval hook from lesson 06 before executing.

4. **OAuth 2.1 PKCE sketch (client-side only).** Add `module3-agent/harness/auth.py`. Implement `pkce_pair() -> tuple[str, str]` (verifier, challenge) using `secrets.token_urlsafe(64)` and SHA-256 + base64url. Implement `validate_audience(token_payload: dict, expected_aud: str) -> bool` — return `False` if `token_payload.get("aud") != expected_aud`. Write two unit tests: one that passes with a matching `aud`, one that fails with a mismatched `aud`. No network calls required — this is a pure-logic sketch.

5. Rebuild the server. Run the full test sequence: linter blocks the poisoned tool, hash pinning detects the mutated description, a non-allowlisted mutation returns an error, and the PKCE unit tests pass.

## Done when

- The server refuses to start if any tool description matches an injection pattern.
- Mutating a tool description in memory and calling `tools/list` again terminates the session with the rug-pull log line.
- Calling a tool not on `MUTATION_ALLOWLIST` returns the allowlist error observation.
- `pkce_pair()` returns a verifier and a base64url-encoded SHA-256 challenge; `validate_audience()` correctly accepts and rejects on `aud` match.
- `npx tsc --noEmit` passes in `mcp-server/`.

## Stretch

Add a minimal gateway stub (`module3-agent/gateway/gateway.ts`) that accepts MCP requests, verifies the Bearer token's `aud` claim against a configured resource URI, and proxies the request to the backend MCP server. Wire it with a `StdioServerTransport` on both ends. Verify: a request with the correct `aud` passes through; one with a wrong `aud` is rejected with a 401 observation.
