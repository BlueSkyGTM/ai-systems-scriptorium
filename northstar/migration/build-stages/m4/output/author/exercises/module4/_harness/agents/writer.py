"""Writer stub agent.

Same module3-agent loop shape as the researcher, different role and tool set. The writer
turns findings into a terse summary. Deterministic stub model so the harness runs offline.
"""

# --- tools ---------------------------------------------------------------------

def _draft(text: str) -> str:
    return f"[draft]\n{text}"

def _read_file(path: str) -> str:
    return f"[contents of {path}] (stubbed)"

TOOLS = {
    "draft": _draft,
    "read_file": _read_file,
}


# --- stub model ----------------------------------------------------------------

def stub_model(messages, turn):
    goal = messages[-1]["content"]
    if turn == 0:
        return {"type": "tool_call", "name": "draft", "args": {"text": goal}}
    return {
        "type": "final",
        "content": f"Summary: {goal[:120]}".rstrip(),
    }


# --- the agent loop ------------------------------------------------------------

def run(goal: str, max_turns: int = 5, trace=None):
    messages = [
        {"role": "system", "content": "You are a writer. Be terse and clear."},
        {"role": "user", "content": goal},
    ]
    for turn in range(max_turns):
        decision = stub_model(messages, turn)
        if decision["type"] == "final":
            if trace is not None:
                trace.append({"turn": turn, "act": "final", "content": decision["content"]})
            return decision["content"]

        name, args = decision["name"], decision["args"]
        result = TOOLS[name](**args)
        observation = f"[{name} result]\n{result}"
        messages.append({"role": "assistant", "content": f"call {name}({args})"})
        messages.append({"role": "tool", "content": observation})
        if trace is not None:
            trace.append({"turn": turn, "act": name, "args": args, "observation": result})

    return "[budget exhausted] no final answer"


if __name__ == "__main__":
    steps = []
    answer = run("three sources reviewed; key points condensed", trace=steps)
    for s in steps:
        print(s)
    print("ANSWER:", answer)
