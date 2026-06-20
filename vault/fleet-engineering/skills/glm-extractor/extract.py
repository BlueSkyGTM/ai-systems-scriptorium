#!/usr/bin/env python3
"""fleet-engineering extractor — GLM runner for a multi-agent governance repo.

Small, dense repo (Module 3 — fleet/multi-agent governance): patterns, stories,
templates (GLM-summarized with safety tags) + verbatim reference docs and JSON
schemas (passthrough). Two modes:

  single      -- one GLM call from a blob you build (patterns, stories, schemas,
                 templates, inventory, curriculum-map, reference summaries).
  passthrough -- MECHANICAL verbatim concat of files under `## <path>` headers
                 (FLEET.md / budget / state / registry "full content as-is").

Universal API truths (see SKILL.md): coding-plan key -> only /api/coding/ (1113
elsewhere = model-not-in-plan); glm-5.x reasoning -> thinking disabled.
"""
import argparse, json, os, random, sys, time, urllib.request, urllib.error

API_URL = "https://api.z.ai/api/coding/paas/v4/chat/completions"
API_KEY = "3ee9e7dff7ca48199128ee2d70e7591d.dQf6EjZtSElYB1vc"
MODEL   = os.environ.get("GLM_MODEL", "glm-5.1")

SYSTEM = (
    "You are a curriculum extraction assistant for a Module 3 'multi-agent & "
    "fleet governance' unit. Fleet engineering = going from one agent to 3+ "
    "loops / 5+ agents: registries, identity, governance, kill switches, budget "
    "guards. Governance is a technical skill here. Read raw repo content and "
    "produce structured markdown in the exact format requested. Faithful; no opinions."
)


def call_glm(user, system=SYSTEM, max_tokens=3000, retries=8):
    body = json.dumps({"model": MODEL, "messages": [
        {"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.3, "max_tokens": max_tokens,
        "thinking": {"type": "disabled"}}).encode()
    last = ""
    for attempt in range(retries):
        rl = False
        try:
            req = urllib.request.Request(API_URL, data=body, headers={
                "Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.load(r)
            c = (d.get("choices", [{}])[0].get("message", {}).get("content", "") or "").strip()
            if c:
                return c
            last = "empty completion (is thinking disabled?)"
        except urllib.error.HTTPError as e:
            try:
                last = e.read().decode()[:200]
            except Exception:
                last = f"HTTP {e.code}"
            rl = "1302" in last or e.code == 429
        except Exception as e:
            last = str(e)[:200]
        time.sleep(min((8 if rl else 2) * (1.7 ** attempt), 45) + random.uniform(0, 2))
    raise RuntimeError(f"GLM call failed after {retries} tries: {last}")


def do_single(args):
    user = open(args.user_file, encoding="utf-8").read()
    out = call_glm(user, max_tokens=args.max_tokens)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write(out.strip() + "\n")
    print(f"[single] {args.out} ({len(out)} bytes)", file=sys.stderr)


def do_passthrough(args):
    parts = []
    if args.header_file:
        parts.append(open(args.header_file, encoding="utf-8").read().rstrip() + "\n")
    for f in args.file:
        parts.append(f"\n## `{f}`\n\n{open(f, encoding='utf-8', errors='replace').read().rstrip()}\n")
    mode = "a" if args.append else "w"
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, mode, encoding="utf-8") as fh:
        fh.write(("\n" if args.append else "") + "\n".join(parts) + "\n")
    print(f"[passthrough] {args.out} ({len(args.file)} files, {'append' if args.append else 'write'})", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="mode", required=True)
    ps = sub.add_parser("single")
    ps.add_argument("--user-file", required=True); ps.add_argument("--out", required=True)
    ps.add_argument("--max-tokens", type=int, default=3000); ps.set_defaults(func=do_single)
    pp = sub.add_parser("passthrough")
    pp.add_argument("--file", nargs="+", required=True); pp.add_argument("--out", required=True)
    pp.add_argument("--header-file", default=""); pp.add_argument("--append", action="store_true")
    pp.set_defaults(func=do_passthrough)
    args = p.parse_args(); args.func(args)


if __name__ == "__main__":
    main()
