# Extra Credit — Enhancers for the Library

The Scriptorium has one job: make the books. This room holds the **enhancers** — optional tools that
make the *learning* better, and nothing else. The name is the rule: extra credit is earned on top of
the work; it never replaces it.

## The Principle: Enhance, Never Overpower

A reader is better served finishing one book straight through than getting a quarter of the way in
because they were fiddling with an add-on. Every enhancer here is **secondary to the curriculum**: it
deepens or sustains the learning (recall, practice, connection) and it stays out of the way of the
reading. The moment an enhancer competes with the books for the reader's attention, it has failed its brief.

The model enhancer is **Open Brain** (the spaced-repetition layer specced in `../progression/`): it
does nothing until a reader *finishes* a course, then it can be injected into any book in the library to
fight the forgetting curve. Added value, on top, opt-in.

## What Belongs Here

- Add-ons that enhance the learning experience across the library: recall and practice (Open Brain),
  exercise-repo generators, artifact connectors, progress and review helpers.
- Each one **born connected** to the logged material (the connect protocol in `CONTEXT.md`), so it is a
  node in the knowledge graph, not an island.

## What Does NOT Belong Here

Be strict; this is the boundary that keeps the repo's role clear. One test: **does it make a reader's
experience of a Library book better?** If no, it is off-mission and gets its own repo. Off-mission,
explicitly, is:

- **Business or operations tooling** — go-to-market, CRM, sales, analytics; anything serving a company
  rather than a learner.
- **Standalone apps or products** that reuse the curriculum's patterns but do not feed a book.
- **Generic utilities** with no tie to a specific book, lesson, or the reader's progress.
- **Experiments unconnected to any book or enhancer** — a probe must point at a real learning use, or it
  does not enter the lab.

These are not lesser; they are *elsewhere*. The Scriptorium stays a book factory plus the enhancers that
serve it. Everything else earns its own home (and, ideally, its own clone of the engine).

## Never From Scratch (Where Enhancers Come From)

An enhancer does not have to be built here from zero, and usually should not be. The preferred path is to
**salvage**: a thing you already built, or a useful component from an external repo you come across.
Either way it enters as an **experiment**, runs through the connect protocol (wired to the logged
material), and earns its way to **production**. The rule is reuse, not greenfield: start from the closest
working thing and adapt it to serve the library.

## Lifecycle: Experiment → Production → Home

1. **Experiment** — a probe, a spike, "does this even work." Throwaway by default.
2. **Production** — once it proves out, it is built for real: runnable, documented, tested, to the
   platform's standards. An enhancer has to earn its way out of experiment before it is production.
3. **Home** — when complete, it graduates to a permanent home in the repo: injected into the library
   (per book) or shelved in the enhancers wing. The two enduring shelves are the **Library** (the
   books) and the **Enhancers** (the completed add-ons).

See `CONTEXT.md` for the routing law and the connect-to-logged-material protocol.
