# The Stages of the Loop

Each round in an interview loop is run by a different person with a different hypothesis. They are not passing the baton; they are each collecting a different kind of evidence. One preparation strategy, applied uniformly, serves none of them well.

The five graded stages that follow each evaluate something distinct, each has a failure mode that is specific to that stage, and each draws on a different piece of your dossier. Know which piece belongs in which room.

## The Recruiter Screen

The recruiter is not evaluating depth. They are running a binary filter: does this person know what they do, and does what they describe fit the role? The screen is usually thirty minutes, and the signal they are collecting is whether you can pitch yourself without friction.

Two things fail here. The first is scope creep: you spend five minutes on context, two on what you built, and then the call ends without a portfolio headline. The second is hedging: "I've worked on a few different things" is the answer that eliminates you, because it signals that you cannot name the most compelling thing you have built and explain it in a sentence.

The dossier pieces that prepare this stage are the portfolio-narrative overview and the answers log. The portfolio-narrative overview is a one-to-two paragraph summary of your strongest artifact that any hiring-stage reader can understand in ninety seconds. The answers log is not merely supplementary here: the grader treats it as a required readiness check for this stage, because the recruiter will often ask you to describe your background or walk through what you have done with AI systems, and the answers log is where you have practiced and calibrated that language. Both pieces need to be in place before you mark this stage ready.

Your preparation goal for this stage is to be able to deliver a two-minute pitch from memory: what you built, why it mattered, and one concrete outcome.

## The Hiring-Manager Round

The hiring manager is not listening to your project walk. They are building a model of how you operate. The questions are behavioral: tell me about a time you owned a difficult problem, tell me about a time you had to influence without authority, tell me about a decision that did not go the way you expected.

The failure mode here is thinness. Candidates who prepare their WHAT (the architecture, the metrics, the stack) but not their HOW (how they decided, how they pushed back, how they recovered) sound technically competent but operationally unreadable. The hiring manager is trying to predict your behavior; they cannot do that from your technical choices.

The dossier piece that prepares this stage is the behavioral bank: a structured set of stories categorized by dimension, built using the Algorithm's decomposition method and calibrated for ownership and influence. Those two calibrate categories need to be READY before this round. Check your calibration scorecard; if ownership or influence is not clean on the latest rep, that gap is what this stage will surface.

## The Systems-Design Round

The systems-design round is the highest-difficulty stage in the loop. The evaluator gives you an open-ended problem, a clock, and very little structure. They are not evaluating whether you have memorized a reference architecture. They are watching how you reason under ambiguity: do you clarify scope before building, do you name the tradeoffs in your choices, do you think about failure modes before they prompt you, and do you connect your design to production constraints?

The failure mode is memorized slides. A candidate who jumps to a solution and recites its components without engaging the problem space fails this round even if the components are correct. What the evaluator hears is that you do not know what you do not know, and that is the signal they are most afraid of.

The dossier piece that prepares this stage is the systems-design log: a set of timed design exercises you have done with the Algorithm's structured method, each ending with a written reasoning trace. The systems-design calibrate category must be READY here. Budget the most reps in this category across your preparation; it has the longest ramp and the most surface area to expose gaps.

## The Portfolio Deep-Dive

The portfolio deep-dive is the round where you walk a real artifact. The evaluator has likely read your resume and your GitHub, and they want to understand the decisions behind what they see. They are not evaluating the artifact; they are evaluating your relationship to it. Can you explain why you made each load-bearing choice, what you would do differently, and what the failure modes are?

The failure mode here is narration without reasoning. "I used a vector store for retrieval" is a statement. "I used a vector store because the query pattern was semantic rather than keyword-based, and that tradeoff meant I had to add a relevance floor to avoid surfacing low-confidence results" is a decision. The evaluator is listening for decisions, not descriptions.

The dossier piece that prepares this stage is the portfolio-narrative document: a decision-by-decision walkthrough of your strongest artifact, written to be narrated under questioning. If the document only describes what you built and not why each choice was the right one given the alternatives, go back and add the why before this round. Module 6's tailoring lesson explains how to enter the same artifact from different decision points depending on the room; this is the stage where that skill pays off directly.

## The Panel

The panel is the stage that mixes everything. It often includes one behavioral question, a light portfolio walk, and at least one question about conflict or failure. The evaluators may be engineers, cross-functional peers, or both, and they are each running a slightly different lens.

The failure mode is inconsistency. A story you told in the behavioral round that does not match your portfolio narrative, an answer about failure that sounds rehearsed rather than honest, or a response to conflict that is too smooth: the panel is the round where gaps between what you practiced in isolation surface as contradictions under combined pressure.

The dossier pieces that prepare this stage are the behavioral bank and the portfolio-narrative document, together. The conflict and failure calibrate categories must be READY; those two dimensions are the ones the panel is most likely to probe, and they are the ones candidates most often under-prepare because they are uncomfortable to practice. Run reps explicitly on conflict and failure stories before this round.

## The Honest Gap: The Technical Coding Screen

Many loops include a technical coding screen: algorithm problems, data structure questions, or language-specific exercises under a timer. That stage is part of the loop but not graded here. The dossier this book builds does not prepare it; the Algorithm, the behavioral bank, the systems-design log, and the portfolio narrative are not substitutes for coding-screen practice.

Source coding-screen preparation separately. LeetCode, NeetCode, and similar structured programs cover this stage directly. Do not assume your dossier readiness translates to coding-screen readiness; they are distinct skills and the loop grades them independently.

## Core Concepts

- Each loop stage is run by a different evaluator with a different hypothesis; one preparation posture does not transfer across stages, and the failure mode at each stage is specific to what that stage is actually measuring.
- The behavioral bank covers two stages (hiring-manager and panel) and must have ownership, influence, conflict, and failure calibrated READY before either round.
- The portfolio-narrative document appears in three stages (recruiter screen, portfolio deep-dive, and panel); one strong document built from decisions and tradeoffs pays off more than any other single dossier artifact.
- The technical coding screen is a real loop stage that this book does not cover; source dedicated coding-screen practice separately and do not conflate dossier readiness with coding-screen readiness.

<div class="claude-handoff" data-exercise="exercises/module8/the-stages-of-the-loop/">

**Try It in Claude Code:** for each stage in your loop plan, write what it evaluates and the specific dossier piece you will lead with, and mark your readiness honestly.

</div>
