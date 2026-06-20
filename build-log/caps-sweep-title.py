#!/usr/bin/env python3
"""Title-case sweep — every major word capitalized, across ALL headings (H1-H3)
and the SUMMARY ToC labels. Reverses the earlier sentence-case pass per Ray.
Preserves acronyms, proper nouns, code identifiers; lowercases minor words
unless first/last. Skips fenced code blocks and backtick-bearing headings.
Default dry-run; --apply to write."""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "library" / "completed" / "sans-python" / "src"

MINOR = {"a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet", "as",
         "at", "by", "in", "of", "on", "to", "up", "off", "per", "via", "vs",
         "with", "from", "into", "onto", "over", "than"}
LOWER_BRANDS = {"tokio", "cargo", "async", "await", "npm", "pip", "uv", "pytest"}
CANON = {"rust": "Rust", "python": "Python", "docling": "Docling", "llama": "Llama",
         "constitutional": "Constitutional", "kubernetes": "Kubernetes",
         "github": "GitHub", "claude": "Claude", "anthropic": "Anthropic",
         "voyager": "Voyager", "letta": "Letta", "reflexion": "Reflexion",
         "guard": "Guard", "zinsser": "Zinsser"}
ROMAN = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"}


def preserve(core):
    if core in ROMAN:
        return core
    if re.match(r'^[A-Z]{2,}', core):                       # MCP, RAG, LLMs, KV
        return core
    if any(c.isdigit() for c in core) and any(c.isupper() for c in core):
        return core                                          # A2A, K8s, P95
    if re.search(r'[A-Z]', core[1:]):                        # TypeScript, LoRA, DevOps
        return core
    low = core.lower()
    if low in LOWER_BRANDS:
        return low
    if low in CANON:
        return CANON[low]
    return None


def cap(core):
    return core[:1].upper() + core[1:].lower()


def do_part(part, force_cap):
    m = re.match(r'^([^0-9A-Za-z]*)(.*?)([^0-9A-Za-z]*)$', part)
    lead, core, trail = m.group(1), m.group(2), m.group(3)
    if not core:
        return part
    p = preserve(core)
    if p is not None:
        return lead + p + trail
    if not force_cap and core.lower() in MINOR:
        return lead + core.lower() + trail
    return lead + cap(core) + trail


def title_case(text):
    if '`' in text:
        return text
    toks = text.split(' ')
    content = [i for i, t in enumerate(toks) if re.search(r'[0-9A-Za-z]', t)]
    if not content:
        return text
    first_i, last_i = content[0], content[-1]
    out = []
    for i, tok in enumerate(toks):
        if not re.search(r'[0-9A-Za-z]', tok):
            out.append(tok)
            continue
        force = (i == first_i or i == last_i)
        if '/' in tok:
            out.append('/'.join(do_part(s, True) for s in tok.split('/')))
        elif '-' in tok and not tok.startswith('-'):
            subs = tok.split('-')
            out.append('-'.join(do_part(s, j == 0 or j == len(subs) - 1)
                                for j, s in enumerate(subs)))
        else:
            out.append(do_part(tok, force))
    return ' '.join(out)


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    apply = '--apply' in sys.argv
    changed_files = 0
    for md in sorted(SRC.rglob('*.md')):
        lines = md.read_text(encoding='utf-8').splitlines(keepends=True)
        in_fence = False
        changed = False
        is_summary = md.name == 'SUMMARY.md'
        for i, line in enumerate(lines):
            s = line.lstrip()
            if s.startswith('```') or s.startswith('~~~'):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if is_summary:
                def repl(m):
                    nonlocal changed
                    new = title_case(m.group(1))
                    if new != m.group(1):
                        changed = True
                        print(f"[ToC] {m.group(1)!r} -> {new!r}")
                    return '[' + new + ']'
                nl = re.sub(r'\[([^\]]+)\]', repl, line)
                if nl != line:
                    lines[i] = nl
            else:
                m = re.match(r'^(#{1,3}) (.*?)(\s*)$', line)
                if m:
                    new = title_case(m.group(2))
                    if new != m.group(2):
                        changed = True
                        print(f"[{m.group(1)}] {md.relative_to(SRC)}: {m.group(2)!r} -> {new!r}")
                        lines[i] = m.group(1) + ' ' + new + '\n'
        if changed:
            changed_files += 1
            if apply:
                md.write_text(''.join(lines), encoding='utf-8')
    print(f"\n{'APPLIED' if apply else 'DRY-RUN'} — {changed_files} files would change.")


if __name__ == '__main__':
    main()
