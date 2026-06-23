# FREEZE-VERIFIED — Weights and Measures M5 Spine

Verified 2026-06-22. `eval_gate.py --selftest` exit 0; all 28 cases pass.

## selftest output

```
eval_gate.py --selftest
[PASS] normalize: lowercase + strip
[PASS] normalize: trailing punct stripped
[PASS] normalize: internal whitespace collapsed
[PASS] normalize: punctuation mid-string preserved

[PASS] exact_match: identical strings
[PASS] exact_match: case-insensitive
[PASS] exact_match: trailing punct ignored
[PASS] exact_match: different strings

[PASS] token_f1: perfect match
[PASS] token_f1: partial overlap
[PASS] token_f1: no overlap
[PASS] token_f1: both empty
[PASS] token_f1: pred empty
[PASS] token_f1: ref empty
[PASS] token_f1: known value 0.8

[PASS] mock_judge: exact match -> 1.0
[PASS] mock_judge: case match -> 1.0
[PASS] mock_judge: high F1 -> 0.8
[PASS] mock_judge: zero overlap -> 0.2

[PASS] perplexity_from_nll: nll=0 -> 1.0
[PASS] perplexity_from_nll: nll=1 -> e
[PASS] perplexity_from_nll: empty -> nan
[PASS] normalise_perplexity: ppl=1.0 -> 1.0
[PASS] normalise_perplexity: ppl=e -> 0.5
[PASS] normalise_perplexity: nan -> 0.0

[PASS] aggregate_scores: all-1 -> 1.0
[PASS] aggregate_scores: all-0 -> 0.0

[PASS] eval_gate: tuned > base -> PASS
[PASS] eval_gate: base > tuned -> BLOCK

selftest: OK
```

## demo output

```
eval_gate.py --demo

 #    EM     F1   Judge     PPL   Agg(T)   Agg(B)
--  ----  -----  ------  ------  -------  -------
 1   1.0  1.000   1.000    1.05   0.9905   0.9887
 2   1.0  1.000   1.000    1.08   0.9860   0.6044
 3   0.0  0.857   0.800    1.09   0.6008   0.3622
 4   0.0  0.833   0.800    1.12   0.5898   0.2139
 5   0.0  0.000   0.200    1.52   0.1812   0.1812

tuned mean aggregate : 0.6697
base  mean aggregate : 0.4701
margin               : 0.01
gate result          : PASS -- promote checkpoint
```

FREEZE-VERIFIED: eval_gate.py selftest OK (28/28), demo OK.
