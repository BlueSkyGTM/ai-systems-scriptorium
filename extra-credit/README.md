# Extra Credit — Enhancers for the Library

The Scriptorium has one job: make the books. This room holds the **enhancers** — optional tools that
make the *learning* better, and nothing else. The name is the rule. Extra credit is earned on top of
the work; it never replaces it.

## The Principle: Enhance, Never Overpower

A reader is better served finishing one book straight through than getting a quarter of the way in
because they were fiddling with a tool. Every enhancer here is **secondary to the curriculum**: it
deepens or sustains the learning (recall, practice, connection) and it stays out of the way of the
reading. The moment a tool competes with the books for the reader's attention, it has failed its brief.

The model enhancer is **Open Brain** (the spaced-repetition layer specced in `../progression/`): it
does nothing until a reader *finishes* a course, then it can be injected into any book in the library to
fight the forgetting curve. Added value, on top, opt-in.

## What Belongs Here

- Tools that enhance the learning experience across the library: recall and practice (Open Brain),
  exercise-repo generators, artifact connectors, progress and review helpers.
- Each one **born connected** to the logged material (the connect protocol in `CONTEXT.md`), so it is a
  node in the knowledge graph, not an island.

## What Does NOT Belong Here

- A general experiment sandbox, or a place to "stay busy between phases." This is not that.
- Anything that does not serve the library's learning. Off-mission work (business tooling, unrelated
  projects) gets its own repo.

## Lifecycle: Experiment → Production → Home

1. **Experiment** — a probe, a spike, "does this even work." Throwaway by default.
2. **Production** — once it proves out, it is built for real: runnable, documented, tested, to the
   platform's standards. A tool has to earn its way out of experiment before it is production.
3. **Home** — when complete, it graduates to a permanent home in the repo: injected into the library
   (per book) or shelved in the enhancers wing. The two enduring shelves are the **Library** (the
   books) and the **Enhancers** (the completed add-ons).

## Pending Cleanup (the "everything else" queue)

- Rename the `tools/` tier to `production/` to match the lifecycle above.
- Decide the disposition of `tools/gtm-ops` — it is off-mission (a go-to-market engine), parked here
  deliberately as a probe to gauge whether this production system can be recreated for other asset
  types. It does not belong in the enhancers lifecycle; it is the seed of a separate question.
- Review `experiments/kv-cache-sizer` and either connect it to a lesson or retire it.
- Name and create the permanent **Enhancers** shelf once the first tool (Open Brain) completes.

See `CONTEXT.md` for the routing law and the connect-to-logged-material protocol.
