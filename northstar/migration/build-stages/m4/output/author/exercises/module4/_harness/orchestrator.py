"""Minimal supervisor orchestrator.

Routes a task to one of two stub agents (researcher, writer) by role, runs that agent's
loop, and collects the result. The control plane is plain Python — no agent framework.

This is the floor. Lesson 03 turns this into a real supervisor-worker system with direct
tool calls and owned context boundaries; the safety lessons add budgets, a kill switch,
and HITL on top. Run offline with the deterministic stub agents:

    python orchestrator.py "summarize the project status"
"""

import sys
from pathlib import Path

from agents import researcher, writer

AGENT_RUNNERS = {
    "researcher": researcher.run,
    "writer": writer.run,
}

REGISTRY_PATH = Path(__file__).parent / "registry.yaml"


# --- registry loading ----------------------------------------------------------

def load_registry(path: Path = REGISTRY_PATH) -> dict:
    """Load registry.yaml. Uses PyYAML if installed; otherwise a tiny stdlib fallback
    that parses just enough of this file's shape so the harness runs with zero installs."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # optional
        return yaml.safe_load(text)
    except ImportError:
        return _minimal_yaml(text)


def _minimal_yaml(text: str) -> dict:
    """Parses only the routing block this harness needs. Not a general YAML parser —
    install PyYAML for the full registry. Returns {'routing': {'default_role', 'roles'}}."""
    roles, default_role, in_roles = {}, "researcher", False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("default_role:"):
            default_role = stripped.split(":", 1)[1].strip()
        elif stripped == "roles:":
            in_roles = True
        elif in_roles and line.startswith("    ") and ":" in stripped:
            key, val = (p.strip() for p in stripped.split(":", 1))
            roles[key] = val
        elif in_roles and not line.startswith("    "):
            in_roles = False
    return {"routing": {"default_role": default_role, "roles": roles}}


# --- routing -------------------------------------------------------------------

def route(task: str, registry: dict) -> str:
    """Map a task to a role. Stub heuristic: keyword match, else the default role.
    Lesson 03 replaces this with a supervisor that plans and delegates via tool calls."""
    routing = registry["routing"]
    lowered = task.lower()
    if any(w in lowered for w in ("write", "summary", "summarize", "draft")):
        return "writer"
    if any(w in lowered for w in ("research", "find", "gather", "investigate")):
        return "researcher"
    return routing["default_role"]


# --- the supervisor ------------------------------------------------------------

def supervise(task: str) -> dict:
    registry = load_registry()
    role = route(task, registry)
    agent_id = registry["routing"]["roles"].get(role, role)
    runner = AGENT_RUNNERS[role]

    trace = []
    result = runner(task, trace=trace)
    return {"task": task, "routed_to": role, "agent_id": agent_id, "result": result, "trace": trace}


if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) or "summarize the project status"
    out = supervise(task)
    print(f"task        : {out['task']}")
    print(f"routed to   : {out['routed_to']} ({out['agent_id']})")
    print("trace       :")
    for step in out["trace"]:
        print(f"  {step}")
    print(f"result      : {out['result']}")
