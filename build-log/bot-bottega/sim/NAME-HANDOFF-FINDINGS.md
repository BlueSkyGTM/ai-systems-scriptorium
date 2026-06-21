# agent-os-starter — Is the Name the Handoff? (A/B interrogation)

Ray's hypothesis: the handoff "ceremony" the agents asked for is just the repo NAME — it reorients a cold
operator into its role, "eliminates the scaffolding," and the rest clicks. Tested A/B: two cold operators
inherit a repo, given ONLY the boot kit + the repo's name; one name strong and role-encoding
(`gtm-signal-engine`), one bland (`repo`).

## Result: the name carries the ROLE handoff. Confirmed.

- **`gtm-signal-engine`**: the agent "snapped into focus" from the name alone — derived the domain, the
  shape (ingest signals -> score/route -> sink), the cadence (scheduled/triggered), and the operating
  POSTURE ("pipeline operator, not strategist; never send outbound without a human gate; every run leaves
  a traceable artifact"). Called the structure "legible from the name alone."
- **`repo`** (control): "carries nothing"; generic process skeleton only; "per the kit's own dud rule,
  this is a dud" at step 1.
- The delta proves the NAME (not the kit) carries the reorientation. Ray is right: a strong name eliminates
  the identity/role scaffolding and the agent assumes its new role from one string.

## But the name cannot carry two things (both agents, even the oriented one)

1. **The builder's frozen DECISIONS.** The `gtm-signal-engine` agent, fully oriented, still could not name
   the signal sources, the sinks + credentials, the dedup/state schema, the specific forbidden actions, or
   the success test. It reached for a `SPEC.md` ("without it, my spec is placeholders, not a contract").
2. **The live STATE.** What already ran, current condition. A name is static; it cannot say "the last run
   half-finished."

## The refined handoff = NAME + SPEC + STATUS

- **NAME** -> role / identity / posture (free; does the reorientation; replaces most of the OPERATOR.md the
  earlier agents wanted).
- **SPEC** -> the builder's decisions, frozen once at build (sources, sinks, thresholds, forbidden actions,
  success test).
- **STATUS / run-log** -> live state (what ran, succeeded / failed / pending), so a cold operator does not
  re-fire a completed action.

"The ceremony is easy" holds: not a manual — a name plus two small files, with the name doing the heavy
lifting.

## Definition of "AI Operating System" (now concrete + testable)

A system whose NAME reorients a cold operator into its role, plus a SPEC of frozen decisions and a live
STATUS, such that a memoryless agent reads name -> spec -> status and operates safely. That is the
falsifiable bar the autoplan reviewers said was missing — arrived at empirically.
