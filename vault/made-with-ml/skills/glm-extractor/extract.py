#!/usr/bin/env python3
"""made-with-ml extractor — GLM single-call runner + notebook-outline helper.

made-with-ml is a Python MLOps *project* (modules, a big notebook, deploy
configs, a Makefile) — NOT a tree of lesson folders. So extraction here is
single-mode: Claude gathers a source blob, GLM writes one structured doc.
There is no per-lesson fan-out and no concurrency to manage; calls are
sequential, so the only API concerns are the universal ones (see SKILL.md):
  - coding-plan key -> only the /api/coding/ endpoint works (1113 elsewhere)
  - glm-5.x are reasoning models -> thinking MUST be disabled or content is empty

Modes:
  single     --user-file F --out F [--max-tokens N] [--system-file F]
             One GLM call from a user-content file you build. Writes the result.
  nb-outline --ipynb F --out F [--max-snippet N]
             MECHANICAL (no GLM): walk a Jupyter notebook and emit, per markdown
             heading cell, the heading + a truncated snippet of the first cell of
             that section. Produces the outline blob you then feed to `single`.
             Never dumps full cell content (madewithml.ipynb is 2.5 MB).
"""
import argparse, json, os, random, sys, time, urllib.request, urllib.error

API_URL = "https://api.z.ai/api/coding/paas/v4/chat/completions"
API_KEY = "3ee9e7dff7ca48199128ee2d70e7591d.dQf6EjZtSElYB1vc"
MODEL   = os.environ.get("GLM_MODEL", "glm-5.1")   # coding-plan; thinking disabled below

SYSTEM_DEFAULT = (
    "You are an MLOps curriculum extraction assistant for a course that teaches "
    "production ML (experiment tracking, serving, monitoring, CI/CD). You read raw "
    "source from the Made-With-ML repo and produce structured markdown docs in the "
    "exact format requested. Focus on the MLOps concepts and the workflow, not "
    "Python syntax. Be precise and faithful; do not invent. No opinions."
)


def call_glm(user, system=SYSTEM_DEFAULT, max_tokens=3000, retries=8):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": 0.3,
        "max_tokens": max_tokens,
        "thinking": {"type": "disabled"},   # critical for glm-5.x reasoning models
    }).encode()
    last = ""
    for attempt in range(retries):
        rate_limited = False
        try:
            req = urllib.request.Request(API_URL, data=body, headers={
                "Authorization": "Bearer " + API_KEY,
                "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.load(r)
            content = (d.get("choices", [{}])[0]
                        .get("message", {}).get("content", "") or "").strip()
            if content:
                return content
            last = "empty completion (is thinking disabled?)"
        except urllib.error.HTTPError as e:
            try:
                last = e.read().decode()[:200]
            except Exception:
                last = f"HTTP {e.code}"
            rate_limited = "1302" in last or e.code == 429
        except Exception as e:
            last = str(e)[:200]
        base = 8 if rate_limited else 2
        time.sleep(min(base * (1.7 ** attempt), 45) + random.uniform(0, 2))
    raise RuntimeError(f"GLM call failed after {retries} tries: {last}")


def do_single(args):
    user = open(args.user_file, encoding="utf-8").read()
    system = open(args.system_file, encoding="utf-8").read() if args.system_file else SYSTEM_DEFAULT
    out = call_glm(user, system=system, max_tokens=args.max_tokens)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out.strip() + "\n")
    print(f"[single] wrote {args.out} ({len(out)} bytes)", file=sys.stderr)


def _src(cell):
    s = cell.get("source", "")
    return "".join(s) if isinstance(s, list) else (s or "")


def do_nb_outline(args):
    nb = json.load(open(args.ipynb, encoding="utf-8"))
    cells = nb.get("cells", [])
    lines = [f"# Notebook outline blob — {os.path.basename(args.ipynb)}",
             f"# {len(cells)} cells total. Heading cells + first-cell snippet per section.\n"]
    n = args.max_snippet
    for i, c in enumerate(cells):
        if c.get("cell_type") != "markdown":
            continue
        src = _src(c).strip()
        first = src.split("\n", 1)[0]
        if not first.lstrip().startswith("#"):
            continue
        # snippet = the rest of this markdown cell, else the next cell's source
        body = src[len(first):].strip()
        if not body and i + 1 < len(cells):
            nxt = cells[i + 1]
            body = _src(nxt).strip()
            kind = nxt.get("cell_type")
        else:
            kind = "markdown"
        body = body.replace("\n", " ")[:n]
        lines.append(f"\n## {first.lstrip('# ').strip()}   [heading level: {first.count('#')}]")
        lines.append(f"FIRST-CELL ({kind}): {body}")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    heads = sum(1 for l in lines if l.lstrip().startswith("## "))
    print(f"[nb-outline] wrote {args.out} ({heads} headings)", file=sys.stderr)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="mode", required=True)

    ps = sub.add_parser("single")
    ps.add_argument("--user-file", required=True)
    ps.add_argument("--out", required=True)
    ps.add_argument("--system-file", default="")
    ps.add_argument("--max-tokens", type=int, default=3000)
    ps.set_defaults(func=do_single)

    pn = sub.add_parser("nb-outline")
    pn.add_argument("--ipynb", required=True)
    pn.add_argument("--out", required=True)
    pn.add_argument("--max-snippet", type=int, default=500)
    pn.set_defaults(func=do_nb_outline)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
