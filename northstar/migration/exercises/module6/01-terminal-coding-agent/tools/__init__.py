"""The tool surface — the only place the model's intentions become real actions.

Three tools, each scoped to a project root so a tool cannot reach outside it:

- ``read_file``  — read a file's text (the model needs to see the bug).
- ``write_file`` — overwrite a file's text (the model fixes the bug).
- ``run_tests``  — run the suite through the subprocess sandbox (observe).

The registry validates the tool name and the arguments before dispatch, runs
the tool, and returns a structured observation string. This is the M3 tool-use
contract (describe / decide / execute / observe) with the execute step pinned
to a project root.
"""

from __future__ import annotations

import json
import os

import sandbox

# JSON Schema contracts the model reads to choose arguments, and the registry
# validates against before dispatch. Kept identical — drift between the schema
# you advertise and the one you check is a silent contract break.
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
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
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
    """Resolve ``rel_path`` against the project root, refusing to escape it.

    The path jail: a tool scoped to a project has no business touching files
    outside it. ``../`` traversal that climbs past the root is denied.
    """
    root = os.path.realpath(project_root)
    target = os.path.realpath(os.path.join(root, rel_path))
    if target != root and not target.startswith(root + os.sep):
        raise ValueError(f"path escapes project root: {rel_path}")
    return target


def read_file(project_root: str, path: str) -> str:
    target = _resolve(project_root, path)
    with open(target, encoding="utf-8") as f:
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
    """Check required fields are present. Returns a list of error strings."""
    schema = TOOL_SCHEMAS[name]["parameters"]
    errors = []
    for key in schema.get("required", []):
        if key not in args:
            errors.append(f"missing required field: {key}")
    return errors


def dispatch(name: str, args: dict, project_root: str) -> str:
    """Validate then execute. Returns a structured observation string.

    Errors come back as observations, not exceptions, so the model can read the
    failure and retry with corrected arguments — the loop never crashes on a
    bad tool call.
    """
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


def schemas_json() -> str:
    """The tool contracts as JSON — what a real model would receive in `tools`."""
    return json.dumps(list(TOOL_SCHEMAS.values()), indent=2)
