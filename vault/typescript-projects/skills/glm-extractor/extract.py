#!/usr/bin/env python3
"""typescript-projects extractor — GLM runner for a TypeScript topic repo.

Module 1 — TypeScript language foundation (the product-layer language: APIs,
agent orchestration, tooling). 15 project topics under `projects/<topic>/`, each
with a README (from the "Learning TypeScript" book). Two modes:

  single  -- one GLM call from a blob (inventory, curriculum map).
  topics  -- fan out one GLM call per `projects/<topic>/README.md`, summarize the
             topic (TS concepts + Sans-Python use case), assembled in order.

Universal API truths (see SKILL.md): coding-plan key -> /api/coding/ only (1113
elsewhere = model-not-in-plan); glm-5.x reasoning -> thinking disabled; RPM 1302
-> throttle + jittered backoff.
"""
import argparse, glob, json, os, random, sys, threading, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "https://api.z.ai/api/coding/paas/v4/chat/completions"
API_KEY = "3ee9e7dff7ca48199128ee2d70e7591d.dQf6EjZtSElYB1vc"
MODEL   = os.environ.get("GLM_MODEL", "glm-5.1")
MAXWORKERS = 6
MIN_INTERVAL = 1.3
_rl = threading.Lock(); _last = [0.0]


def _throttle():
    with _rl:
        w = _last[0] + MIN_INTERVAL - time.time()
        if w > 0:
            time.sleep(w)
        _last[0] = time.time()


SYSTEM = (
    "You are a curriculum extraction assistant for a TypeScript language-"
    "foundation module in an AI systems course. TypeScript is the product-layer "
    "language: APIs, agent orchestration, tooling, type-safe schemas, MCP "
    "contracts. Read raw topic READMEs and produce structured markdown in the "
    "exact format requested. Faithful; no opinions."
)


def call_glm(user, system=SYSTEM, max_tokens=1100, retries=8):
    body = json.dumps({"model": MODEL, "messages": [
        {"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.3, "max_tokens": max_tokens,
        "thinking": {"type": "disabled"}}).encode()
    last = ""
    for attempt in range(retries):
        _throttle(); rl = False
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
        time.sleep(min((8 if rl else 2) * (1.7 ** attempt), 45) + random.uniform(0, 3))
    raise RuntimeError(f"GLM call failed after {retries} tries: {last}")


def do_single(args):
    user = open(args.user_file, encoding="utf-8").read()
    out = call_glm(user, max_tokens=args.max_tokens)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write(out.strip() + "\n")
    print(f"[single] {args.out} ({len(out)} bytes)", file=sys.stderr)


def do_topics(args):
    instr = open(args.instr_file, encoding="utf-8").read()
    header = open(args.header_file, encoding="utf-8").read() if args.header_file else ""
    topics = sorted(d for d in glob.glob(os.path.join(args.topics_dir, "*")) if os.path.isdir(d))
    print(f"[topics] {args.topics_dir}: {len(topics)} topics -> {args.out}", file=sys.stderr)

    def work(td):
        name = os.path.basename(td.rstrip("/"))
        rp = next((p for p in (os.path.join(td, "README.md"), os.path.join(td, "readme.md")) if os.path.exists(p)), None)
        text = open(rp, encoding="utf-8", errors="replace").read() if rp else ""
        if not text.strip():
            return name, f"\n## {name}\n_[NO README]_\n"
        user = f"{instr}\n\n---\nTOPIC FOLDER: `{name}`\n---\nREADME:\n\n{text}\n"
        try:
            return name, call_glm(user, max_tokens=args.max_tokens).strip() + "\n"
        except Exception as e:
            return name, f"\n## {name}\n_[GLM EXTRACTION FAILED: {e}]_\n"

    results = {}
    with ThreadPoolExecutor(max_workers=MAXWORKERS) as ex:
        futs = {ex.submit(work, t): t for t in topics}
        done = 0
        for fut in as_completed(futs):
            name, sec = fut.result(); results[name] = sec; done += 1
            print(f"  [{done}/{len(topics)}] {name}", file=sys.stderr)
    ordered = [results[os.path.basename(t.rstrip('/'))] for t in topics]
    out = (header.rstrip() + "\n\n" if header else "") + "\n".join(ordered)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write(out)
    fails = sum(1 for s in ordered if "FAILED" in s or "NO README" in s)
    print(f"[topics] {args.out} ({len(out)} bytes, {fails} flagged)", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="mode", required=True)
    ps = sub.add_parser("single")
    ps.add_argument("--user-file", required=True); ps.add_argument("--out", required=True)
    ps.add_argument("--max-tokens", type=int, default=3000); ps.set_defaults(func=do_single)
    pt = sub.add_parser("topics")
    pt.add_argument("--topics-dir", required=True); pt.add_argument("--out", required=True)
    pt.add_argument("--instr-file", required=True); pt.add_argument("--header-file", default="")
    pt.add_argument("--max-tokens", type=int, default=1100); pt.set_defaults(func=do_topics)
    args = p.parse_args(); args.func(args)


if __name__ == "__main__":
    main()
