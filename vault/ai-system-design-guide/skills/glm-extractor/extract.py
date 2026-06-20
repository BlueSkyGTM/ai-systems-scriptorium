#!/usr/bin/env python3
"""ai-system-design-guide extractor — GLM runner for a markdown chapter guide.

This repo is a markdown systems-design guide: chapter folders (NN-name/) each
holding numbered section files (NN-section.md), plus a few huge root files
(two ~3,400-line eval guides). So extraction has three modes:

  chapter   -- fan out one concurrent GLM call per *.md section file in a chapter
               folder, assemble the returned markdown sections in order under a
               header. (The workhorse — like the lesson-phase orchestrator, but
               the unit is a markdown file, not docs/en.md.)
  single    -- one GLM call from a user-content blob you build (tables, derived
               docs, interview list).
  headings  -- MECHANICAL (no GLM): emit the markdown heading tree of a file
               (up to --max-level), with line numbers. Feeds `single` for the
               structure-only targets (eval guides, antilibrary, interview).

Universal API truths (see SKILL.md): coding-plan key -> only /api/coding/ works
(1113 elsewhere = model-not-in-plan); glm-5.x are reasoning models -> thinking
MUST be disabled. RPM limit = error 1302 -> throttle + jittered backoff.
"""
import argparse, glob, json, os, random, re, sys, threading, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "https://api.z.ai/api/coding/paas/v4/chat/completions"
API_KEY = "3ee9e7dff7ca48199128ee2d70e7591d.dQf6EjZtSElYB1vc"
MODEL   = os.environ.get("GLM_MODEL", "glm-5.1")
MAXWORKERS = 6
MIN_INTERVAL = 1.3      # seconds between request starts -> stays under the RPM limit (1302)

_rl_lock = threading.Lock()
_last = [0.0]


def _throttle():
    with _rl_lock:
        wait = _last[0] + MIN_INTERVAL - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()


SYSTEM = (
    "You are a curriculum extraction assistant for an AI systems-design course. "
    "You read raw markdown chapters from a systems-design guide and produce "
    "structured markdown documentation in the exact format requested. Be precise, "
    "comprehensive, and follow formatting instructions exactly. Write clear "
    "technical English. Do not add opinions or recommendations -- extract faithfully."
)


def call_glm(user, system=SYSTEM, max_tokens=1400, retries=8):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": 0.3,
        "max_tokens": max_tokens,
        "thinking": {"type": "disabled"},
    }).encode()
    last = ""
    for attempt in range(retries):
        _throttle()
        rate_limited = False
        try:
            req = urllib.request.Request(API_URL, data=body, headers={
                "Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.load(r)
            content = (d.get("choices", [{}])[0].get("message", {}).get("content", "") or "").strip()
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
        time.sleep(min(base * (1.7 ** attempt), 45) + random.uniform(0, 3))
    raise RuntimeError(f"GLM call failed after {retries} tries: {last}")


def do_chapter(args):
    instr = open(args.instr_file, encoding="utf-8").read()
    header = open(args.header_file, encoding="utf-8").read() if args.header_file else ""
    inc = re.compile(args.include) if args.include else None
    exc = re.compile(args.exclude) if args.exclude else None

    files = []
    for f in sorted(glob.glob(os.path.join(args.chapter_dir, "*.md"))):
        b = os.path.basename(f)
        if inc and not inc.search(b):
            continue
        if exc and exc.search(b):
            continue
        files.append(f)
    print(f"[chapter] {args.chapter_dir}: {len(files)} files -> {args.out}", file=sys.stderr)

    def work(path):
        name = os.path.basename(path)
        text = open(path, encoding="utf-8", errors="replace").read()
        if not text.strip():
            return name, f"\n### {name}\n_[NO SOURCE — file empty]_\n"
        user = f"{instr}\n\n---\nSECTION FILE: `{name}`\n---\nSOURCE:\n\n{text}\n"
        try:
            return name, call_glm(user, max_tokens=args.max_tokens).strip() + "\n"
        except Exception as e:
            return name, f"\n### {name}\n_[GLM EXTRACTION FAILED: {e}]_\n"

    results = {}
    with ThreadPoolExecutor(max_workers=MAXWORKERS) as ex:
        futs = {ex.submit(work, f): f for f in files}
        done = 0
        for fut in as_completed(futs):
            name, sec = fut.result()
            results[name] = sec
            done += 1
            print(f"  [{done}/{len(files)}] {name}", file=sys.stderr)

    ordered = [results[os.path.basename(f)] for f in files]
    out = (header.rstrip() + "\n\n" if header else "") + "\n".join(ordered)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write(out)
    fails = sum(1 for s in ordered if "FAILED" in s or "NO SOURCE" in s)
    print(f"[done] {args.out} ({len(out)} bytes, {fails} flagged)", file=sys.stderr)


def do_single(args):
    user = open(args.user_file, encoding="utf-8").read()
    system = open(args.system_file, encoding="utf-8").read() if args.system_file else SYSTEM
    out = call_glm(user, system=system, max_tokens=args.max_tokens)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write(out.strip() + "\n")
    print(f"[single] {args.out} ({len(out)} bytes)", file=sys.stderr)


def do_headings(args):
    out_lines = [f"# Heading tree — {os.path.basename(args.file)}"]
    incode = False
    with open(args.file, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if line.lstrip().startswith("```"):
                incode = not incode
                continue
            if incode:
                continue
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m and len(m.group(1)) <= args.max_level:
                out_lines.append(f"{m.group(1)} [L{i}] {m.group(2).strip()}")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write("\n".join(out_lines) + "\n")
    print(f"[headings] {args.out} ({len(out_lines)-1} headings)", file=sys.stderr)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="mode", required=True)

    pc = sub.add_parser("chapter")
    pc.add_argument("--chapter-dir", required=True)
    pc.add_argument("--out", required=True)
    pc.add_argument("--header-file", default="")
    pc.add_argument("--instr-file", required=True)
    pc.add_argument("--include", default="")
    pc.add_argument("--exclude", default="")
    pc.add_argument("--max-tokens", type=int, default=1400)
    pc.set_defaults(func=do_chapter)

    ps = sub.add_parser("single")
    ps.add_argument("--user-file", required=True)
    ps.add_argument("--out", required=True)
    ps.add_argument("--system-file", default="")
    ps.add_argument("--max-tokens", type=int, default=3500)
    ps.set_defaults(func=do_single)

    ph = sub.add_parser("headings")
    ph.add_argument("--file", required=True)
    ph.add_argument("--out", required=True)
    ph.add_argument("--max-level", type=int, default=3)
    ph.set_defaults(func=do_headings)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
