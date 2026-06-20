#!/usr/bin/env python3
"""ai-performance-engineering extractor — GLM runner for an O'Reilly book repo.

This repo is a GPU/performance book: 20 chapter folders (each a README.md +
code we do NOT extract) plus root docs and a checklist. The curriculum seam is
the INFERENCE-SERVING subset only (ch15-20); training/CUDA/kernels (ch01-14)
are antilibrary. Several targets are VERBATIM passthrough (docs, FULL_SWEEP),
not summaries. So three modes:

  single     -- one GLM call from a user-content blob (inventory, antilibrary).
  chapters   -- for each chapter README, GLM extracts a "key concepts +
                hands-on tasks" block; assembled as `## chNN · Title` + that
                block + (with --append-readme) the FULL README verbatim.
  passthrough-- MECHANICAL (no GLM): concatenate given files verbatim, each
                under a `## <title>` header. For "full content preserved" targets.

Universal API truths (see SKILL.md): coding-plan key -> only /api/coding/
(1113 elsewhere = model-not-in-plan); glm-5.x reasoning -> thinking disabled;
RPM limit = 1302 -> throttle + jittered backoff.
"""
import argparse, glob, json, os, random, re, sys, threading, time, urllib.request, urllib.error
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
    "You are a curriculum extraction assistant for an AI performance-engineering "
    "course. The seam is INFERENCE SERVING (cost/token, throughput/dollar, vLLM/"
    "SGLang/TensorRT-LLM, KV cache, paged attention, profiling inference "
    "bottlenecks) -- students deploy and benchmark, they do NOT write GPU kernels. "
    "Read raw book chapter content and produce structured markdown in the exact "
    "format requested. Be precise and faithful; no opinions."
)


def call_glm(user, system=SYSTEM, max_tokens=1200, retries=8):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": 0.3, "max_tokens": max_tokens,
        "thinking": {"type": "disabled"},
    }).encode()
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


def _title(readme_path, fallback):
    for l in open(readme_path, encoding="utf-8", errors="replace"):
        if l.startswith("# "):
            return l.lstrip("# ").strip()
    return fallback


def do_single(args):
    user = open(args.user_file, encoding="utf-8").read()
    out = call_glm(user, max_tokens=args.max_tokens)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write(out.strip() + "\n")
    print(f"[single] {args.out} ({len(out)} bytes)", file=sys.stderr)


def do_chapters(args):
    instr = open(args.instr_file, encoding="utf-8").read()
    header = open(args.header_file, encoding="utf-8").read() if args.header_file else ""
    dirs = sorted(args.chapter_dir)

    def work(d):
        rp = os.path.join(d, "README.md")
        name = os.path.basename(d.rstrip("/"))
        if not os.path.exists(rp):
            return name, f"\n## {name}\n_[NO README]_\n"
        readme = open(rp, encoding="utf-8", errors="replace").read()
        title = _title(rp, name)
        user = f"{instr}\n\n---\nCHAPTER: `{name}` — {title}\n---\nREADME:\n\n{readme}\n"
        try:
            block = call_glm(user, max_tokens=args.max_tokens).strip()
        except Exception as e:
            block = f"_[GLM EXTRACTION FAILED: {e}]_"
        sec = f"\n## {name} · {title}\n\n{block}\n"
        if args.append_readme:
            sec += f"\n<details><summary>Full chapter README (verbatim)</summary>\n\n{readme}\n\n</details>\n"
        return name, sec

    results = {}
    with ThreadPoolExecutor(max_workers=MAXWORKERS) as ex:
        futs = {ex.submit(work, d): d for d in dirs}
        done = 0
        for fut in as_completed(futs):
            name, sec = fut.result(); results[name] = sec; done += 1
            print(f"  [{done}/{len(dirs)}] {name}", file=sys.stderr)
    ordered = [results[os.path.basename(d.rstrip('/'))] for d in dirs]
    out = (header.rstrip() + "\n" if header else "") + "".join(ordered)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write(out)
    fails = sum(1 for s in ordered if "FAILED" in s or "NO README" in s)
    print(f"[chapters] {args.out} ({len(out)} bytes, {fails} flagged)", file=sys.stderr)


def do_passthrough(args):
    header = open(args.header_file, encoding="utf-8").read() if args.header_file else ""
    parts = [header.rstrip() + "\n"] if header else []
    for f in args.file:
        text = open(f, encoding="utf-8", errors="replace").read()
        parts.append(f"\n## `{f}`\n\n{text.rstrip()}\n")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write("\n".join(parts) + "\n")
    print(f"[passthrough] {args.out} ({len(args.file)} files)", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="mode", required=True)
    ps = sub.add_parser("single")
    ps.add_argument("--user-file", required=True); ps.add_argument("--out", required=True)
    ps.add_argument("--max-tokens", type=int, default=3000); ps.set_defaults(func=do_single)

    pc = sub.add_parser("chapters")
    pc.add_argument("--chapter-dir", nargs="+", required=True)
    pc.add_argument("--out", required=True)
    pc.add_argument("--instr-file", required=True)
    pc.add_argument("--header-file", default="")
    pc.add_argument("--append-readme", action="store_true")
    pc.add_argument("--max-tokens", type=int, default=1200); pc.set_defaults(func=do_chapters)

    pp = sub.add_parser("passthrough")
    pp.add_argument("--file", nargs="+", required=True)
    pp.add_argument("--out", required=True)
    pp.add_argument("--header-file", default=""); pp.set_defaults(func=do_passthrough)

    args = p.parse_args(); args.func(args)


if __name__ == "__main__":
    main()
