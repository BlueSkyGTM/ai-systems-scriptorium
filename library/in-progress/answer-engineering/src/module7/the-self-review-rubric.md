# The Self-Review Rubric

A rubric you grade yourself on generously is a rubric that lies. It tells you what you want to hear, confirms the readiness you already feel, and leaves the real gaps exactly where they were before you picked up the pen.

The self-review rubric in `calibrate.py` is designed to prevent that. It is not a checklist you eyeball; it is a schema that scores each of your four Algorithm steps as strong, partial, or weak, and it counts the marks honestly whether you like the count or not. Your job is to apply that schema to your own reps before the scorer ever sees them, and to apply it without inflation.

## Why the Four Algorithm Steps Are the Scoring Axes

The rubric scores the four steps you already know: Decompose, Signal, Construct, Stress-test. Those are not arbitrary categories. They map to the four places an interview answer can break: you misread the question, you aimed at the wrong signal, you built a generic answer, or you left the weakest part undefended. A rep that passes all four is a rep that could not have been better without more knowledge. A rep that fails one tells you exactly where to drill.

Each step has one job in the Algorithm. Each step therefore has one failure mode in the rubric. Scoring them separately keeps the diagnosis precise. If you collapsed all four into a single "how did that go?" rating, you would always average your strengths against your weaknesses and never fix either.

## The Strong/Partial/Weak Scale, Step by Step

These definitions are what `calibrate.py` expects you to have applied before you write your scores into the log. Read them as a decision procedure, not as aspirational descriptions.

**Decompose.** This step asks: did you surface the real question inside the question asked?

- Strong: you named the latent signal or hypothesis the question is designed to surface, not just the surface topic. For an "ownership" question, strong means you identified that the interviewer is collecting evidence of initiative taken without a mandate, not just "tell me about a project you owned."
- Partial: you got the surface ask right but stopped there. You knew it was a behavioral question about ownership and structured your answer accordingly. You did not name what specifically the interviewer is trying to separate strong candidates from weak candidates on.
- Weak: you answered the literal words of the question without decomposing it at all. The question was a container you filled without examining what it was designed to hold.

**Signal.** This step asks: did you aim your answer at what the interviewer is actually collecting?

- Strong: you identified the specific evidence the interviewer needs to mark "yes" on this signal, and you pointed your answer directly at that evidence. You knew, going in, what a yes looks like and built toward it.
- Partial: you had a general sense of the category (influence, conflict, failure) and shaped your answer in that direction, but you could not have named the specific evidence the question is designed to surface before you started speaking.
- Weak: you answered without identifying any target signal. The answer may have been competent, but it was not aimed; you were hoping the signal would emerge from the content rather than building toward it.

**Construct.** This step asks: did you build toward the signal with specific, unfakeable evidence?

- Strong: every claim in the answer is grounded in a detail only you could supply. The numbers, the names, the constraints, the decision you made under pressure: these cannot be recycled from a generic template. A weak candidate with the same job title could not give the same answer.
- Partial: the structure is correct and the story follows the right shape, but the specifics are thin. "I aligned the team around the goal" instead of "I ran three working sessions over two weeks to get the backend lead and the data team to a shared definition of done, because they had been operating on different assumptions about what the feature required." The first is a label; the second is evidence.
- Weak: you rambled, recited the question back, or gave a sequence of assertions without grounding any of them in real detail. The answer has shape but no substance the interviewer can weigh.

**Stress-test.** This step asks: did you find and fix the part a weak candidate could also have said?

- Strong: you found the weakest sentence in your answer, the one that sounds like a competent answer but contains no specific evidence, and you replaced it with something unfakeable. You named the specific reason your contribution was necessary, not just present.
- Partial: you noticed the weak point. You might have flagged it to yourself: "that part was vague." You did not fix it before the answer ended. Noticing is not the same as drilling.
- Weak: no stress-test. The answer ended without you looking for the sentence a weak candidate could also have given. The weakest part is still in the answer, unexamined.

## How to Score Honestly

Partial is the honest default. Not because you are a bad candidate, but because partial is what a solid, well-structured answer that lacks the final layer of specificity looks like. Most reps from most candidates in preparation are partial on at least two steps. That is not discouraging; it is information.

Strong is earned, not assigned. You earned a strong on a step when you can point to the specific thing you did in that rep that passes the step's test: the latent signal you named before answering, the unfakeable detail you embedded in the construct, the weak sentence you found and replaced. If you cannot point to it, the mark is partial.

Weak is information, not failure. A weak mark on Stress-test across five reps tells you Stress-test is your drill target. That is exactly what the rubric is for. The candidate who assigns weak marks accurately and drills them is better off than the candidate who assigns partial to everything and never identifies a drill target.

The inflation trap works like this: you finish a rep that went reasonably well, and you score it strong/strong/strong/partial because it felt clean and you do not want to assign weak marks to a rep you are proud of. Then you do it again on the next rep. After ten reps scored this way, `calibrate.py` shows no weak steps and a readiness verdict that does not match what happens when you try the same questions cold. The trap is not dishonesty; it is the same availability bias that makes the feeling of readiness unreliable. You remember the strong parts and assign the score from the feeling.

The countermeasure is simple: score before you read the verdict. Write your four marks into the log before you run the scorer. If you score after seeing output, you will curve. Write the marks, commit to them, then run. The harsh mark you assigned before the output is the honest one.

## Worked Scoring Example

Here is a practice answer to the question: "Tell me about a time you had to influence a decision you didn't have authority over."

The answer: "I was on a team where we were about to launch a feature without doing performance testing because the timeline was tight. I thought that was risky, so I put together a quick analysis showing what could go wrong and shared it with the tech lead. They agreed we should do the testing, and we found some issues before launch."

Now score each step.

**Decompose: partial.** The candidate correctly identified this as an influence question and built an answer about influencing a technical decision. What they did not name is the specific signal the question is collecting: evidence of influence exercised across an authority gap, with a real cost to the decision-maker. "Told the tech lead and they agreed" is low-resistance influence. It does not show the candidate navigating resistance, making a case to someone with competing priorities, or absorbing a cost to see the decision land right. The surface ask was answered; the latent signal was not.

**Signal: partial.** The candidate aimed at "influence" as a category. They did not aim at the specific evidence the question needs: that the candidate can move a decision when the person who holds it has a reason not to move. The answer describes agreement, not persuasion under resistance. The signal was identified at the category level but not at the specificity level needed to earn a strong mark.

**Construct: partial.** The structure is sound. The setup is clear, the action is present, the outcome is named. But "put together a quick analysis" is a label. What was in the analysis? What numbers, what scenarios, what made it persuasive rather than just concerning? "Found some issues" is the same problem: what issues, at what severity, and what would have happened at launch? The answer has shape with thin specifics.

**Stress-test: weak.** The candidate did not stress-test this answer. The weakest sentence, "They agreed we should do the testing," is also the most important one, and it goes completely unexamined. A weak candidate who had simply raised a concern to a tech lead could give exactly this answer. The stress-test step requires finding that sentence and replacing it with evidence that the tech lead had a reason to say no and here is what the candidate did about that reason. The answer ended without that move.

The log entry for this rep reads:

```
**Decompose:**    partial
**Signal:**       partial
**Construct:**    partial
**Stress-test:**  weak
```

That is an honest score. The answer was not bad; it was a solid first draft with a clear drill target: Stress-test, because the weakest claim is the one that proves nothing. The next rep on an influence question should build specifically toward the moment of resistance.

## Core Concepts

- The four scoring dimensions map directly to the four Algorithm steps: Decompose, Signal, Construct, Stress-test. Each step has one failure mode; each failure mode is a specific drill target.
- Partial is the honest default. Strong is earned by pointing to the specific thing you did in that step; if you cannot point to it, the mark is partial.
- Weak is information: a weak mark across multiple reps on the same step names your drill target with more precision than any amount of rereading.
- Score before you run the scorer. The mark you write before seeing `calibrate.py`'s output is the one that keeps the calibration loop honest.

<div class="claude-handoff" data-exercise="exercises/module7/the-self-review-rubric/">

**Try It in Claude Code:** re-score three reps in your deliberate-practice log strictly against the rubric, downgrading any step you cannot defend as strong, and write one line on what a strong version of each weak step would require.

</div>
