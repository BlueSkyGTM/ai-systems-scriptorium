#!/usr/bin/env python3
"""loop-engineering-orange-book extractor — PDF structure extractor + GLM.

This repo is a PDF companion book (Module 3 reference). The job is STRUCTURE
only (TOC / part / section headings + page numbers) — NOT full text. The PDF is
a Chromium HTML->PDF export with no embedded outline, so the TOC is recovered
from the text.

  pdf-toc -- MECHANICAL. Extract the table of contents to markdown: try the
             embedded outline first; fall back to parsing the "Contents" page
             (Part headers + section headers) and map each section to its start
             page via per-page text scan. Never dumps body prose.
  single  -- one GLM call from a blob (e.g. a 2-sentence README summary).

Deps: pdftotext (poppler) and pypdf. Universal API truths apply for `single`
(coding-plan key /api/coding/ only; glm-5.x -> thinking disabled).
"""
import argparse, json, os, random, re, subprocess, sys, time, urllib.request, urllib.error

API_URL = "https://api.z.ai/api/coding/paas/v4/chat/completions"
API_KEY = "3ee9e7dff7ca48199128ee2d70e7591d.dQf6EjZtSElYB1vc"
MODEL   = os.environ.get("GLM_MODEL", "glm-5.1")


def call_glm(user, system="You extract and summarize faithfully. No opinions.",
             max_tokens=800, retries=8):
    body = json.dumps({"model": MODEL, "messages": [
        {"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.3, "max_tokens": max_tokens,
        "thinking": {"type": "disabled"}}).encode()
    last = ""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(API_URL, data=body, headers={
                "Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.load(r)
            c = (d.get("choices", [{}])[0].get("message", {}).get("content", "") or "").strip()
            if c:
                return c
            last = "empty completion"
        except urllib.error.HTTPError as e:
            last = (e.read().decode()[:200] if True else f"HTTP {e.code}")
        except Exception as e:
            last = str(e)[:200]
        time.sleep(min(2 * (1.7 ** attempt), 30) + random.uniform(0, 2))
    raise RuntimeError(f"GLM call failed: {last}")


def _outline(pdf):
    try:
        import pypdf
        ol = pypdf.PdfReader(pdf).outline
        out = []
        def walk(o, d=0):
            for it in o:
                if isinstance(it, list):
                    walk(it, d + 1)
                else:
                    out.append(("  " * d) + "- " + getattr(it, "title", "?"))
        if ol:
            walk(ol)
        return out
    except Exception:
        return []


def do_pdf_toc(args):
    pdf = args.pdf
    pages = subprocess.run(["pdftotext", "-layout", pdf, "-"],
                           capture_output=True, text=True).stdout.split("\f")
    # The contents page = the page with the most § lines. Each section's body
    # start = its first § occurrence AFTER the contents page.
    sec_re = re.compile(r'^\s*§\s*0*(\d+)')  # body headers may lack a space: "§06Loops…"
    counts = [sum(1 for ln in pg.split("\n") if sec_re.match(ln)) for pg in pages]
    toc_page = (counts.index(max(counts)) + 1) if counts else 0
    sec_page = {}
    for pno, pg in enumerate(pages, 1):
        if pno <= toc_page:
            continue
        for line in pg.split("\n"):
            m = sec_re.match(line)
            if m and m.group(1) not in sec_page:
                sec_page[m.group(1)] = pno
    # Build the TOC by scanning the whole document in order. The Contents block
    # precedes the body; the body then repeats §01... — so the FIRST occurrence
    # of each section number is its TOC entry. Stop when a section number repeats
    # (body start) or all sections are collected.
    toc, seen = [], set()
    for line in "\n".join(pages).split("\n"):
        s = line.strip()
        mp = re.match(r'^(Part\s+\d+\s*[·.\-].*)$', s)
        ms = re.match(r'^§\s*(\d+)\s+(.+)$', s)
        if mp and ("part", s) not in [(k, t) for k, t, _ in toc]:
            toc.append(("part", s.rstrip(), None))
        elif ms:
            num = ms.group(1)
            if num in seen:
                break  # body repeat -> TOC finished
            seen.add(num)
            toc.append(("sec", f"§{num.zfill(2)}  {ms.group(2).strip()}", sec_page.get(num.lstrip('0') or '0')))

    out = [f"# Orange Book — Structure (TOC)", "",
           f"> Source: `{os.path.basename(pdf)}` ({len(pages)} pages). Structure only — TOC, parts, and section headings with start pages. No embedded outline ({'found' if _outline(pdf) else 'Chromium export'}); recovered from the Contents page + per-page scan.", ""]
    ol = _outline(pdf)
    if ol:
        out.append("## Embedded Outline\n")
        out += ol
        out.append("")
    out.append("## Table of Contents\n")
    for kind, text, page in toc:
        if kind == "part":
            out.append(f"\n### {text}")
        else:
            out.append(f"- {text}" + (f"  _(p. {page})_" if page else ""))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write("\n".join(out) + "\n")
    nsec = sum(1 for k, _, _ in toc if k == "sec")
    print(f"[pdf-toc] {args.out} ({nsec} sections, {sum(1 for k,_,_ in toc if k=='part')} parts)", file=sys.stderr)


def do_single(args):
    user = open(args.user_file, encoding="utf-8").read()
    out = call_glm(user, max_tokens=args.max_tokens)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "w", encoding="utf-8").write(out.strip() + "\n")
    print(f"[single] {args.out} ({len(out)} bytes)", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="mode", required=True)
    pt = sub.add_parser("pdf-toc")
    pt.add_argument("--pdf", required=True); pt.add_argument("--out", required=True)
    pt.set_defaults(func=do_pdf_toc)
    ps = sub.add_parser("single")
    ps.add_argument("--user-file", required=True); ps.add_argument("--out", required=True)
    ps.add_argument("--max-tokens", type=int, default=800); ps.set_defaults(func=do_single)
    args = p.parse_args(); args.func(args)


if __name__ == "__main__":
    main()
