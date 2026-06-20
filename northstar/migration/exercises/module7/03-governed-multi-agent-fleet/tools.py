"""The coder node's tool surface — where intent becomes a real file action.

Reused from the M6 coding agent (artifact 01). Three tools, each scoped to a
project root so a tool cannot reach outside it:

- ``read_file``  — read a file's text (see the bug),
- ``write_file`` — overwrite a file's text (fix the bug),
- ``run_tests``  — run the suite through the subprocess sandbox (observe).

The registry validates the tool name and arguments before dispatch and returns a
structured observation string; a bad call comes back as an observation the model
can correct, not an exception that kills the run. In the fleet, the set of tools
a node may call is *also* gated by the registry's per-agent permissions — see
``policy.authorize`` — so a node cannot call a tool outside its declared grant.
"""

from __future__ import annotations

import os

import sandbox

TOOL_SCHEMAS = {
    "read_file": {
        "name": "read_file",
        "description": "Read a UTF-8 text file relative to the project root.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    "write_file": {
        "name": "write_file",
        "description": "Overwrite a UTF-8 text file relative to the project root.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    "run_tests": {
        "name": "run_tests",
        "description": "Run the project's pytest suite in the subprocess sandbox.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}


def _resolve(project_root: str, rel_path: str) -> str:
    """Resolve ``rel_path`` against the project root, refusing to escape it."""
    root = os.path.realpath(project_root)
    target = os.path.realpath(os.path.join(root, rel_path))
    if target != root and not target.startswith(root + os.sep):
        raise ValueError(f"path escapes project root: {rel_path}")
    return target


def read_file(project_root: str, path: str) -> str:
    with open(_resolve(project_root, path), encoding="utf-8") as f:
        return f.read()


def write_file(project_root: str, path: str, content: str) -> str:
    target = _resolve(project_root, path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
    return f"wrote {len(content)} chars to {path}"


def run_tests(project_root: str) -> str:
    result = sandbox.run_pytest(project_root)
    tail = (result.stdout + result.stderr).strip()
    return f"exit_code={result.exit_code} timed_out={result.timed_out}\n{tail}"


def _validate(name: str, args: dict) -> list[str]:
    schema = TOOL_SCHEMAS[name]["parameters"]
    return [f"missing required field: {k}" for k in schema.get("required", []) if k not in args]


def dispatch(name: str, args: dict, project_root: str) -> str:
    """Validate then execute. Returns a structured observation string; errors
    come back as observations so the loop never crashes on a bad tool call."""
    if name not in TOOL_SCHEMAS:
        return f"[error] unknown tool: {name}"
    errors = _validate(name, args)
    if errors:
        return f"[error] invalid args: {'; '.join(errors)}"
    try:
        if name == "read_file":
            return read_file(project_root, args["path"])
        if name == "write_file":
            return write_file(project_root, args["path"], args["content"])
        if name == "run_tests":
            return run_tests(project_root)
    except Exception as exc:  # tool failure becomes an observation
        return f"[error] tool execution failed: {exc}"
    return f"[error] unreachable: {name}"
