# Debugging Out Loud

Getting stuck is not a failure. Going silent when you do is.

The moment a candidate stops talking, the interviewer's job becomes much harder: they cannot tell whether the candidate is thinking clearly and needs a minute, or is lost and starting to thrash. A well-run screen ends with the interviewer saying "I could see exactly how they were thinking, even when it got hard." A failed screen ends with "they went quiet, rewrote it from scratch, and I still don't know how they work." The code at the end matters less than you expect. The narration is the signal.

This lesson is about that moment. You will hit a bug in a screen. When you do, there is a repeatable motion that turns the stuck point into evidence of a systematic mind: gather what you know, form three to five hypotheses, isolate the cause, then fix it and verify. The rest of the lesson works two real bugs through that motion in full.

## The Debugging Motion

The motion has four steps, and each one has a narration line.

**Gather.** Before you change anything, describe the symptom. What is the observable failure? When does it happen? Is it deterministic or intermittent? A candidate who says "so the call is hanging, and it hangs every time, even on a trivial input" has already told the interviewer something useful. The interviewer knows you are not guessing yet.

**Hypothesize.** Generate three to five candidate causes, out loud, before you start eliminating. This step is where most candidates short-circuit: they see one plausible cause and dive in. If they are wrong, they have wasted time and shown the interviewer they do not think systematically. Listing the hypotheses first costs ten seconds and shows a completely different kind of mind. Say each one in a sentence, and say what it would predict.

**Diagnose.** Pick the fastest hypothesis to eliminate and isolate it. Add a temporary check, narrow the input to the smallest case that reproduces the bug, or trace where a value changes. One variable at a time. Narrate each move as you make it: "I'm going to pass an empty string here to rule out an encoding issue" is cleaner than silent typing followed by a result.

**Fix and Verify.** When you have the cause, state it before you patch it. Then fix, and say what a passing verification looks like before you run it. "I expect this to return a structured result now, not hang" is a committed prediction, and committed predictions are what distinguish an engineer from a guesser.

## The Subprocess Sandbox Hangs

Here is the scenario. You have implemented a subprocess sandbox that runs a test suite inside a child process and returns the result. When you call it during the screen, the program hangs. The interviewer is watching.

Start with the gather step. The symptom is a hang on every call, not an exception. The program does not crash; it waits. That rules out a configuration error that would fail immediately.

Now hypothesize, out loud:

1. "The timeout parameter was never passed, so there is no deadline."
2. "The timeout is being passed but the exception is not caught, so it propagates and crashes the agent loop rather than returning a result."
3. "The child process is hanging on output: it is writing more to stdout or stderr than the pipe buffer holds, and `subprocess.run` is blocking on the drain."
4. "The process timed out but the child was not killed, so the parent is stuck waiting for a process that is still running."

That is four hypotheses. You have not touched the code yet. The interviewer has just watched you reason about subprocess semantics from first principles.

Now isolate. The fastest check is whether the `timeout` argument is being passed at all. Look at the call site:

```python
def run(argv: list[str], cwd: str, timeout_s: float = 30.0) -> SandboxResult:
    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
```

The timeout is there. So hypothesis one is eliminated. Now check whether the exception branch exists and returns rather than re-raises:

```python
    except subprocess.TimeoutExpired as exc:
        return SandboxResult(
            exit_code=TIMED_OUT,
            stdout=exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            stderr=(exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
            + "\n[sandbox] wall-clock timeout exceeded",
            timed_out=True,
        )
```

That branch exists and returns a `SandboxResult`. Hypothesis two is eliminated. The hang is happening before the deadline fires, which points toward hypothesis three: the child is producing so much output that the pipe buffer fills and the child blocks trying to write, while the parent blocks waiting for the process to finish. They deadlock.

The fix is `capture_output=True`, which is already present in this implementation. In a screen where the call was written without it, that is the patch: capture both streams so the pipe never blocks. And the deeper lesson, which you should say out loud: a timeout is only useful if you also capture the output, because a full pipe prevents the timeout from ever firing.

State what you expect before you verify: "With capture in place and a short input, I expect the call to return in under a second with `timed_out=False` and a non-empty exit code." Then run it. The motion is gather, hypothesize, diagnose, fix, verify. You have shown the interviewer all five steps with narration.

One implementation detail worth noting: `exc.stdout` on a `TimeoutExpired` exception holds whatever partial output was captured before the deadline. The sandbox in `sandbox.py` decodes it carefully because it can arrive as bytes even though the parent requested text mode. That partial output is often the most useful debugging signal the agent has. Treating a timeout as a `SandboxResult` with `timed_out=True` rather than letting it raise means the agent loop reads it as an observation and can decide whether to retry.

## The Path Jail Has a Hole

Here is the second scenario. You have implemented a tool dispatcher that restricts file access to a project root. During the screen, you demonstrate it, and then the interviewer asks: "What happens if the model passes `../../etc/passwd` as the path argument?" You test it. The restriction holds. Then they ask: "What if the path starts with the root but then escapes?" You test it. The restriction fails.

Gather: the containment check is not catching all traversals. The symptom is specific and the interviewer has pointed you at the input class that triggers it.

Hypothesize:

1. "The path is being joined with the root before being resolved, so a path that starts with an absolute prefix overwrites the join."
2. "The path is being resolved before being joined, which means `realpath` sees the attacker's path in isolation and `os.path.join` appends it after."
3. "The containment check compares strings before resolving symlinks, so a symlink inside the project root could point outside it and pass the check."
4. "The check uses `startswith` with the root string, and a path that starts with the root as a string prefix but then escapes is not caught."

Look at the actual `_resolve` function:

```python
def _resolve(project_root: str, rel_path: str) -> str:
    root = os.path.realpath(project_root)
    target = os.path.realpath(os.path.join(root, rel_path))
    if target != root and not target.startswith(root + os.sep):
        raise ValueError(f"path escapes project root: {rel_path}")
    return target
```

Walk through the order of operations. `root` is resolved first, which flattens symlinks. Then `os.path.join(root, rel_path)` is called before resolving the target; if `rel_path` is a relative path with traversal like `../../../etc/passwd`, the join produces a path outside the root. Then `realpath` resolves the target, which resolves any remaining traversal. The containment check runs on the resolved target.

That means hypothesis four is eliminated: the implementation appends the separator to the root string in the `startswith` check, so a path like `/project-root-and-something-else/file` would not pass. And hypothesis two is eliminated: the resolution order is join-then-resolve, not resolve-then-join. The more interesting case is hypothesis three. Narrate it: "A symlink inside the project root that points to a file outside it would be followed by `realpath`, and the resolved target would fail the containment check. That is correct behavior: the jail catches it."

The actual hole the interviewer is probing is subtler. Pass a path of `subdir/../../etc/passwd`. The join produces `/project-root/subdir/../../etc/passwd`. Then `realpath` resolves it to `/etc/passwd`. The containment check fires: `/etc/passwd` does not start with `/project-root/`, so it raises. The jail works.

Now try a symlink attack differently: create a file inside the root that is a symlink to a file outside it. `realpath` follows the symlink, and the resolved path escapes the root. The jail catches that too.

The hole the interviewer is likely pointing at in a broken implementation is missing the separator in the `startswith` check: a root of `/project` and a path resolving to `/project-extended/secret` would pass a check written as `target.startswith(root)`. The correct implementation appends `os.sep`:

```python
if target != root and not target.startswith(root + os.sep):
    raise ValueError(f"path escapes project root: {rel_path}")
```

This is in the actual `_resolve` function in `tools/__init__.py`. State it explicitly: "The separator is load-bearing. Without it, a directory name that starts with the root string but is a sibling, not a child, would pass the check." That is the fix and the verification in one sentence.

When the interviewer asks you to verify, write a direct test: construct a `project_root`, call `_resolve` with a traversal path, and assert that a `ValueError` is raised. Then call it with a valid relative path and assert it returns the resolved absolute path. State the expected outcome before you run. That is what systematic verification looks like in a screen.

## Recovering Without a Rewrite

When you identify the bug, the instinct is often to scrap what you have and start over. Resist it. A rewrite is expensive and signals that you did not understand your own code. A targeted patch signals that you do.

The question to ask yourself, out loud if there is time: is this a logic error in one function, or is it a structural problem that will require changing several call sites? A containment check that uses `startswith` without the separator is a one-line fix in `_resolve`. A design that puts the path resolution in the wrong layer, so that every caller is responsible for it, is a structural problem. In a screen, patch the logic error in place. Name the structural problem if it exists, propose what a real refactor would look like, and keep moving.

How to say this to the interviewer: "I can see the issue is isolated to the containment check, so I will fix it there rather than rework the whole dispatch flow. If this were production code I would also add a test that exercises the separator edge case, so a future change cannot quietly regress it."

That sentence tells the interviewer three things: you found the bug, you are not panicking, and you think about regressions. That is the screen won.

## Core Concepts

- Going silent when you get stuck is the failure, not the bug itself; narrating the hypotheses and the elimination sequence turns a stumble into evidence of systematic thinking.
- The debugging motion is gather (describe the symptom), hypothesize (three to five candidates, stated before you eliminate any), diagnose (isolate by eliminating the fastest hypothesis first), then fix and verify with a committed prediction.
- A subprocess timeout is only useful if you also capture output; a full pipe prevents the deadline from firing, and treating `TimeoutExpired` as a structured result rather than a raised exception keeps the agent loop readable.
- A path-jail containment check must append `os.sep` to the root in the `startswith` comparison; without it, a sibling directory whose name begins with the root string passes the check and escapes the jail.

---

<div class="claude-handoff" data-exercise="exercises/module4/debugging-out-loud/">

**Try It in Claude Code:** run a coding-screen rep where you deliberately hit a bug, narrate the gather-hypothesize-diagnose-verify motion out loud, and log the stuck point and your recovery in your coding-screen log.

</div>
