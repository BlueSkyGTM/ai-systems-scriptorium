# Behavioral Bank

Copy this file to `behavioral-bank.md` and complete all four story entries, one per category.
The worked example below shows the expected format and the level of detail required.
Remove this instruction block and the worked example before running the validator.

---

<!-- WORKED EXAMPLE: read this to understand the format, then fill in Story 1-4 below with YOUR own stories -->

## Story 0

**Category:** ownership

**Situation:** I pushed to replace our retrieval pipeline with a pure long-context approach across two design reviews. The argument was that newer models could handle our corpus in-context without retrieval overhead. The team committed a quarter to the migration partly on my conviction.

**Task:** I owned proving the new system out before full cutover and running the evaluation that would decide whether to proceed.

**Action:** I ran the eval. Quality matched the baseline, but cost ran four times my projection: cache hit rates collapsed under our update frequency and p95 latency doubled. My first instinct was to tune my way out of it. After two weeks of marginal gains I stopped. I wrote a one-page memo with the numbers, stated plainly that my recommendation had been wrong on the economics, and proposed a hybrid: long-context for small static corpora, retrieval for everything else. I presented it to the same audience I had originally convinced.

**Result:** The hybrid was adopted. We salvaged about 60% of the migration work. The postmortem produced a new team rule: any architecture pitch must include a cost model under realistic update patterns, not just a quality benchmark.

**Learning:** Conviction is useful for getting decisions made and dangerous for unmaking them. I now attach explicit kill criteria to my own proposals so that walking back is a checkpoint I wrote in advance, not a confession I make after running out of options.

**Audit verdict:** Pitfalls checked: vague ownership -- absent ("I pushed," "I ran the eval," "I wrote the memo" carry first-person accountability throughout); buried result -- absent (hybrid adopted and postmortem rule appear in the Result step); missing failure signal -- absent ("cost ran 4x projection," "cache hit rates collapsed under update frequency"); no structural lesson -- absent ("any architecture pitch must include a cost model" is a named team-level practice change). Basic bar: passes -- "cost ran 4x projection," "two weeks of marginal gains before I stopped," "one-page memo stating plainly the recommendation was wrong" are specific enough that a weak candidate cannot replicate them by paraphrasing. Staff bar: passes at the low end -- the postmortem rule applies to the team, not only to the candidate, but it is not clear whether it became a review checklist, a shared template, or a standard adopted by other teams. One specific thing added after audit: the Result step originally ended at "salvaged 60% of the work" with no mention of the team rule; the team rule was added to make the organizational artifact explicit.

---

## Story 1

**Category:** ownership

**Situation:** <fill in your own situation here>

**Task:** <fill in your own task here>

**Action:** <fill in your own action here>

**Result:** <fill in your own result here>

**Learning:** <fill in your own learning here>

**Audit verdict:** <fill in after running the M2 weak-answer audit: pitfalls present/absent, basic bar verdict, staff bar verdict, one specific thing you added or changed>

---

## Story 2

**Category:** conflict

**Situation:** <fill in your own situation here>

**Task:** <fill in your own task here>

**Action:** <fill in your own action here>

**Result:** <fill in your own result here>

**Learning:** <fill in your own learning here>

**Audit verdict:** <fill in after running the M2 weak-answer audit: pitfalls present/absent, basic bar verdict, staff bar verdict, one specific thing you added or changed>

---

## Story 3

**Category:** failure

**Situation:** <fill in your own situation here>

**Task:** <fill in your own task here>

**Action:** <fill in your own action here>

**Result:** <fill in your own result here>

**Learning:** <fill in your own learning here>

**Audit verdict:** <fill in after running the M2 weak-answer audit: pitfalls present/absent, basic bar verdict, staff bar verdict, one specific thing you added or changed>

---

## Story 4

**Category:** influence

**Situation:** <fill in your own situation here>

**Task:** <fill in your own task here>

**Action:** <fill in your own action here>

**Result:** <fill in your own result here>

**Learning:** <fill in your own learning here>

**Audit verdict:** <fill in after running the M2 weak-answer audit: pitfalls present/absent, basic bar verdict, staff bar verdict, one specific thing you added or changed>
