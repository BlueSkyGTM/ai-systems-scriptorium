#!/usr/bin/env python3
"""Em-dash removal across the book's lessons, per Ray (em-dashes read as an AI tell).
Rules: in the "... It in Claude Code" handoff CTA the dash becomes a colon (:);
everywhere else in prose it becomes a semicolon (;). Module-divider H1s
("# Module N — Title") become a colon. Skips fenced code blocks and table rows
(where a lone — is a placeholder, not punctuation). Default dry-run; --apply writes."""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "library" / "completed" / "sans-python" / "src"
EM = "—"


def main():
    apply = "--apply" in sys.argv
    before = after = 0
    changed_files = 0
    for md in sorted(SRC.rglob("*.md")):
        with open(md, encoding="utf-8", newline="") as fh:
            lines = fh.read().splitlines(keepends=True)
        in_fence = False
        changed = False
        for i, line in enumerate(lines):
            s = line.lstrip()
            if s.startswith("```") or s.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence or s.startswith("|"):      # skip code + table rows
                before += line.count(EM)
                after += line.count(EM)
                continue
            before += line.count(EM)
            if EM not in line:
                continue
            new = line
            # 1. handoff CTA dash -> colon
            if "It in Claude Code**" in new:
                new = new.replace("It in Claude Code** " + EM + " ", "It in Claude Code**: ", 1)
            # 2. module-divider H1 dash -> colon
            elif re.match(r"^# Module ", new):
                new = new.replace(" " + EM + " ", ": ", 1)
            # 3. parenthetical pair ( — aside — ) -> commas (no sentence-ender/; /: inside)
            pair = " " + EM + r" ([^" + EM + r".!?;:]+?) " + EM + " "
            new = re.sub(pair, r", \1, ", new)
            # 4. remaining single dash (clause join / elaboration) -> semicolon
            new = new.replace(" " + EM + " ", "; ")
            after += new.count(EM)
            if new != line:
                lines[i] = new
                changed = True
        if changed:
            changed_files += 1
            if apply:
                with open(md, "w", encoding="utf-8", newline="") as fh:
                    fh.write("".join(lines))
    print(f"em-dashes before: {before}  after: {after}  ({'APPLIED' if apply else 'DRY-RUN'}, {changed_files} files)")


if __name__ == "__main__":
    main()
