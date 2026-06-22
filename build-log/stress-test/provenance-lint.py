#!/usr/bin/env python3
"""Provenance-token lint — a HARD gate for the one ceiling defect the pilot caught mechanically.

The pilot found cheap-fleet lessons leaking build-pipeline / source tokens into reader-facing prose
("Question type: Collaboration and Conflict (asdg 05, Example 4)"). That is a STYLE violation (machine
tokens belong in fenced blocks, never inline) AND it is mechanically detectable, so it does not need
the expensive ceiling grader. This is the soft-gate -> hard-gate migration in action.

Scans markdown for source/provenance tokens in PROSE (outside fenced code blocks and outside the
`<div class="claude-handoff">` machine block). Exits 1 if any are found.

Usage:  python provenance-lint.py <file-or-dir> [<file-or-dir> ...]
"""
import re
import sys
import pathlib

# Patterns that should never appear in reader-facing prose. These are workshop/source tokens.
PATTERNS = [
    re.compile(r"\basdg\b", re.IGNORECASE),                 # source repo id leak
    re.compile(r"\(\s*asdg[^)]*\)", re.IGNORECASE),         # "(asdg 05, Example 4)"
    re.compile(r"\bthe ore\b", re.IGNORECASE),              # workshop term leak
    re.compile(r"\bbehavioral bank\b", re.IGNORECASE),      # ingredient name leak
    re.compile(r"\bExample\s+\d+\s+in the\b", re.IGNORECASE),  # "Example 5 in the behavioral bank"
    re.compile(r"^\s*Question type\s*:", re.IGNORECASE),    # leaked source header
]

def lint_file(path: pathlib.Path):
    hits = []
    in_fence = False
    in_handoff = False
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if 'class="claude-handoff"' in line:
            in_handoff = True
        if in_handoff and stripped.startswith("</div>"):
            in_handoff = False
            continue
        if in_fence or in_handoff:
            continue
        for pat in PATTERNS:
            if pat.search(line):
                hits.append((n, line.strip()[:100]))
                break
    return hits

def main(argv):
    targets = []
    for arg in argv:
        p = pathlib.Path(arg)
        if p.is_dir():
            targets.extend(sorted(p.rglob("*.md")))
        elif p.suffix == ".md":
            targets.append(p)
    total = 0
    for path in targets:
        for n, snippet in lint_file(path):
            print(f"{path}:{n}: provenance token in prose -> {snippet}")
            total += 1
    if total:
        print(f"\nFAIL: {total} provenance-token leak(s) in prose across {len(targets)} file(s).")
        return 1
    print(f"PASS: no provenance-token leaks in {len(targets)} file(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["."]))
