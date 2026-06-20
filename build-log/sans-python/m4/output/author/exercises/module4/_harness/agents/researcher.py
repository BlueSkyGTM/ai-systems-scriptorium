"""Researcher stub agent.

Reuses the module3-agent loop shape: Observe -> Think -> Act, with a message buffer,
a tiny tool registry, a stop condition, and a turn budget. The "model" is a deterministic
stub so the harness runs offline. Swap `stub_model` for a real model call to go live; the
loop shape does not change.
"""

# --- tools (the agent's hands) -------------------------------------------------

def _search(query: str) -> str:
    # Deterministic canned result. Replace with a real search tool when going live.
    return f"[sources for '{query}'] three relevant findings located."

def _read_file(path: str) -> str:
    return f"[contents of {path}] (stubbed)"

TOOLS = {
    "search": _search,
    "read_file": _read_file,
}


# --- the stub model (deterministic, offline) -----------------------------------

def stub_model(messages, turn):
    """Return a fake model decision. Turn 0: call search. Turn 1: final answer.

    A real model call would take `messages` and return either a tool call or a final
    answer. This stub hard-codes that two-step shape so the loop runs without an API key.
    """
    goal = messages[-1]["content"]
    if turn == 0:
        return {"type": "tool_call", "name": "search", "args": {"query": goal}}
    return {
        "type": "final",
        "content": f"Findings on '{goal}': three sources reviewed; key points condensed.",
    }


# --- the agent loop (module3-agent shape) --------------------------------------

def run(goal: str, max_turns: int = 5, trace=None):
    """Run the researcher on `goal`. Returns the final answer string.

    `trace` (optional list) collects Observe/Think/Act steps for inspection.
    """
    messages = [
        {"role": "system", "content": "You are a researcher. Gather and condense."},
        {"role": "user", "content": goal},
    ]
    for turn in range(max_turns):
        decision = stub_model(messages, turn)
        if decision["type"] == "final":
            if trace is not None:
                trace.append({"turn": turn, "act": "final", "content": decision["content"]})
            return decision["content"]

        name, args = decision["name"], decision["args"]
        result = TOOLS[name](**args)            # Act
        observation = f"[{name} result]\n{result}"  # observation formatter
        messages.append({"role": "assistant", "content": f"call {name}({args})"})
        messages.append({"role": "tool", "content": observation})
        if trace is not None:
            trace.append({"turn": turn, "act": name, "args": args, "observation": result})

    return "[budget exhausted] no final answer"


if __name__ == "__main__":
    steps = []
    answer = run("project status", trace=steps)
    for s in steps:
        print(s)
    print("ANSWER:", answer)
