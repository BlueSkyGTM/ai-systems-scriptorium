#!/usr/bin/env python3
"""One-shot sentence-case sweep for Sans Python.

Touches ONLY H1 page titles (`# `) across src/ and the ToC labels in
SUMMARY.md. H2/H3 are already sentence case and are left untouched.
Run with --apply to write; default is dry-run (prints before -> after).
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "library" / "completed" / "sans-python" / "src"

# Single-initial-cap proper nouns the heuristic would otherwise lowercase.
PRESERVE = {
    "rust", "python", "docling", "llama", "constitutional", "kubernetes",
    "github", "claude", "anthropic", "voyager", "letta", "reflexion",
    "guard", "zinsser", "mem0", "memgpt",
}
ROMAN = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"}


def fix_part(part, is_first_word, preserve_single_upper=False):
    """Sentence-case a single hyphen/slash subpart."""
    if not part:
        return part
    lead = re.match(r'^[^0-9A-Za-z]*', part).group(0)
    trail = re.search(r'[^0-9A-Za-z]*$', part).group(0)
    core = part[len(lead):len(part) - len(trail)] if trail else part[len(lead):]
    if not core:
        return part

    keep = False
    if core in ROMAN:
        keep = True
    elif preserve_single_upper and len(core) == 1 and core.isupper():
        keep = True                                # A/B, AI in a slash compound
    elif re.match(r'^[A-Z]{2,}', core):           # acronym: MCP, RAG, LLMs, KV
        keep = True
    elif any(ch.isdigit() for ch in core) and any(ch.isupper() for ch in core):
        keep = True                                # A2A, K8s, P95
    elif re.search(r'[A-Z]', core[1:]):           # internal cap: TypeScript, LoRA, DevOps
        keep = True
    elif core.lower() in PRESERVE:
        keep = True
        core = {p: p for p in []}.get(core, core)  # canonical handled below

    if keep:
        # canonical casing for known single-cap proper nouns
        canon = {
            "rust": "Rust", "python": "Python", "docling": "Docling",
            "llama": "Llama", "constitutional": "Constitutional",
            "kubernetes": "Kubernetes", "github": "GitHub", "claude": "Claude",
            "anthropic": "Anthropic", "voyager": "Voyager", "letta": "Letta",
            "reflexion": "Reflexion", "guard": "Guard", "zinsser": "Zinsser",
        }
        if core.lower() in canon and not re.search(r'[A-Z]', core[1:]) \
                and not any(c.isdigit() for c in core):
            core = canon[core.lower()]
        return lead + core + trail

    core = core.lower()
    if is_first_word:
        core = core[0].upper() + core[1:]
    return lead + core + trail


def sentence_case(text):
    if '`' in text:        # leave code-bearing headings alone
        return text
    tokens = text.split(' ')
    out = []
    first_done = False
    for tok in tokens:
        if tok == '' or not re.search(r'[0-9A-Za-z]', tok):
            out.append(tok)              # pure punctuation (—, &, +, /)
            continue
        is_first = not first_done
        first_done = True
        # process hyphen/slash subparts; only the very first subpart of the
        # first word gets the leading capital
        if '/' in tok:
            sub = tok.split('/')
            tok = '/'.join(fix_part(s, is_first and i == 0, preserve_single_upper=True)
                           for i, s in enumerate(sub))
        elif '-' in tok and not tok.startswith('-'):
            sub = tok.split('-')
            tok = '-'.join(fix_part(s, is_first and i == 0) for i, s in enumerate(sub))
        else:
            tok = fix_part(tok, is_first)
        out.append(tok)
    return ' '.join(out)


def main():
    apply = '--apply' in sys.argv
    changes = 0
    for md in sorted(SRC.rglob('*.md')):
        lines = md.read_text(encoding='utf-8').splitlines(keepends=True)
        changed = False
        is_summary = md.name == 'SUMMARY.md'
        in_fence = False
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.startswith('```') or stripped.startswith('~~~'):
                in_fence = not in_fence
                continue
            if in_fence:
                continue          # never touch `# comment` lines inside code
            if is_summary:
                def repl(m):
                    nonlocal changed
                    new = sentence_case(m.group(1))
                    if new != m.group(1):
                        changed = True
                        print(f"[ToC] {m.group(1)!r} -> {new!r}")
                    return '[' + new + ']'
                newline = re.sub(r'\[([^\]]+)\]', repl, line)
                if newline != line:
                    lines[i] = newline
            else:
                m = re.match(r'^# (?!#)(.*?)(\s*)$', line)
                if m:
                    new = sentence_case(m.group(1))
                    if new != m.group(1):
                        changed = True
                        print(f"[H1] {md.relative_to(SRC)}: {m.group(1)!r} -> {new!r}")
                        lines[i] = '# ' + new + m.group(2) + '\n' if not line.endswith('\n') else '# ' + new + '\n'
        if changed:
            changes += 1
            if apply:
                md.write_text(''.join(lines), encoding='utf-8')
    print(f"\n{'APPLIED' if apply else 'DRY-RUN'} — {changes} files would change.")


if __name__ == '__main__':
    main()
