"""Registry loading + pure-Python schema validation — no third-party deps.

Governance-as-code means the registry is a contract a machine validates in CI
before it governs anything (M4 lesson 13). This module is that validator, written
to the hard constraint of the BUILD->TEST gate: **standard library only.**

Two jobs:

1. ``load_registry`` reads ``registry.yaml``. It uses PyYAML if installed; if not,
   it falls back to a tiny purpose-built parser that handles exactly this file's
   shape (the same approach the M4 harness uses) so the smoke path needs zero
   installs.

2. ``validate`` checks the loaded registry against ``schemas/registry.schema.json``
   using a small JSON Schema subset implemented here — ``required``, ``type``,
   ``enum``, ``minItems``, ``minLength``, ``exclusiveMinimum``, ``additionalProperties``,
   ``items``, ``properties``, and ``$ref``/``$defs``. Enough to catch a malformed
   registry; it guards an optional ``jsonschema`` import for the real thing.

A malformed registry raises ``RegistryError`` here, before the fleet runs a single
action. That is the floor every other governance check stands on.
"""

from __future__ import annotations

import json
import os
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(HERE, "registry.yaml")
SCHEMA_PATH = os.path.join(HERE, "schemas", "registry.schema.json")


class RegistryError(Exception):
    """A registry that fails to load or validate. Stops the fleet before it runs."""


# --- loading -------------------------------------------------------------------

def load_registry(path: str = REGISTRY_PATH) -> dict:
    """Load and validate the registry. Returns the parsed dict or raises."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        import yaml  # optional; not required on the smoke path
        data = yaml.safe_load(text)
    except ImportError:
        data = _minimal_yaml(text)
    validate(data)
    return data


def _minimal_yaml(text: str) -> dict:
    """Parse the subset of YAML this registry uses: scalars, nested maps, and a
    list of maps under ``agents``. Not a general parser — install PyYAML for that.
    It handles the exact two-and-three-level indentation in registry.yaml."""
    root: dict = {}
    agents: list = []
    current_agent: dict | None = None
    current_perms: dict | None = None
    fleet_gates: dict = {}
    in_fleet_gates = False

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # top-level key
        if indent == 0 and not stripped.startswith("-"):
            in_fleet_gates = False
            current_agent = None
            current_perms = None
            if stripped == "agents:":
                continue
            if stripped == "fleet_gates:":
                in_fleet_gates = True
                root["fleet_gates"] = fleet_gates
                continue
            key, _, val = stripped.partition(":")
            root[key.strip()] = _scalar(val.strip())
            continue

        # fleet_gates children
        if in_fleet_gates and indent >= 2 and ":" in stripped:
            key, _, val = stripped.partition(":")
            fleet_gates[key.strip()] = _scalar(val.strip())
            continue

        # new agent list item
        if stripped.startswith("- "):
            current_agent = {}
            current_perms = None
            agents.append(current_agent)
            stripped = stripped[2:]
            key, _, val = stripped.partition(":")
            current_agent[key.strip()] = _scalar(val.strip())
            continue

        # agent fields and nested permissions
        if current_agent is not None:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if key == "permissions" and val == "":
                current_perms = {}
                current_agent["permissions"] = current_perms
                continue
            # deeper indent than the agent's own fields => inside permissions
            if current_perms is not None and indent >= 6:
                current_perms[key] = _scalar(val)
                continue
            current_perms = None
            current_agent[key] = _scalar(val)

    if agents:
        root["agents"] = agents
    return root


def _scalar(val: str) -> Any:
    """Coerce a YAML scalar: bools, ints, floats, inline lists, else string."""
    if val == "":
        return ""
    if val in ("true", "True"):
        return True
    if val in ("false", "False"):
        return False
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [_scalar(p.strip()) for p in inner.split(",")]
    try:
        if "." in val:
            return float(val)
        return int(val)
    except ValueError:
        return val.strip('"').strip("'")


# --- validation (pure-Python JSON Schema subset) -------------------------------

def validate(data: Any, schema_path: str = SCHEMA_PATH) -> None:
    """Validate ``data`` against the registry JSON Schema. Raises RegistryError.

    Prefers the real ``jsonschema`` library if it happens to be installed; falls
    back to the in-module subset validator so the gate stays stdlib-only.
    """
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    try:
        import jsonschema  # optional; the gate does not require it
        try:
            jsonschema.validate(data, schema)
            return
        except jsonschema.ValidationError as exc:  # pragma: no cover - needs the lib
            raise RegistryError(f"registry failed validation: {exc.message}") from exc
    except ImportError:
        errors = _check(data, schema, schema, "$")
        if errors:
            raise RegistryError("registry failed validation:\n  - " + "\n  - ".join(errors))


def _resolve_ref(ref: str, root_schema: dict) -> dict:
    """Resolve a local ``#/$defs/...`` pointer against the root schema."""
    assert ref.startswith("#/")
    node: Any = root_schema
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _check(data: Any, schema: dict, root_schema: dict, path: str) -> list[str]:
    """Return a list of human-readable validation errors (empty == valid)."""
    errors: list[str] = []

    if "$ref" in schema:
        return _check(data, _resolve_ref(schema["$ref"], root_schema), root_schema, path)

    expected = schema.get("type")
    if expected and not _type_ok(data, expected):
        errors.append(f"{path}: expected {expected}, got {type(data).__name__}")
        return errors  # type wrong — deeper checks are noise

    if expected == "object" or isinstance(data, dict):
        for key in schema.get("required", []):
            if not isinstance(data, dict) or key not in data:
                errors.append(f"{path}: missing required field '{key}'")
        props = schema.get("properties", {})
        if isinstance(data, dict):
            if schema.get("additionalProperties") is False:
                for key in data:
                    if key not in props:
                        errors.append(f"{path}: unexpected field '{key}'")
            for key, subschema in props.items():
                if key in data:
                    errors += _check(data[key], subschema, root_schema, f"{path}.{key}")

    if expected == "array" or isinstance(data, list):
        if isinstance(data, list):
            if "minItems" in schema and len(data) < schema["minItems"]:
                errors.append(f"{path}: needs at least {schema['minItems']} item(s)")
            item_schema = schema.get("items")
            if item_schema:
                for i, item in enumerate(data):
                    errors += _check(item, item_schema, root_schema, f"{path}[{i}]")

    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: {data!r} not in {schema['enum']}")
    if "minLength" in schema and isinstance(data, str) and len(data) < schema["minLength"]:
        errors.append(f"{path}: string shorter than {schema['minLength']}")
    if "exclusiveMinimum" in schema and isinstance(data, (int, float)) and not isinstance(data, bool):
        if data <= schema["exclusiveMinimum"]:
            errors.append(f"{path}: {data} must be > {schema['exclusiveMinimum']}")

    return errors


def _type_ok(data: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(data, dict)
    if expected == "array":
        return isinstance(data, list)
    if expected == "string":
        return isinstance(data, str)
    if expected == "boolean":
        return isinstance(data, bool)
    if expected == "number":
        return isinstance(data, (int, float)) and not isinstance(data, bool)
    if expected == "integer":
        return isinstance(data, int) and not isinstance(data, bool)
    return True
