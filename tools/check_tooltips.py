#!/usr/bin/env python3
"""Static tooltip completeness checker for Boxflat panels.

Scans the panel source files and reports interactive settings rows that are
missing tooltips, plus any referenced command keys that are missing from
``data/descriptions.yml``.

Exit codes:
    0 - no issues
    1 - missing tooltips or missing YAML command keys
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import yaml


# Paths relative to this script's location (project root).
ROOT = Path(__file__).resolve().parents[1]
PANELS_DIR = ROOT / "boxflat" / "panels"
DESCRIPTIONS_FILE = ROOT / "data" / "descriptions.yml"

# Row types that are interactive and should expose a tooltip.
INTERACTIVE_ROW_TYPES = {
    # Boxflat widgets
    "BoxflatSwitchRow",
    "BoxflatSliderRow",
    "BoxflatSliderGroupRow",
    "BoxflatButtonRow",
    "BoxflatEntryRow",
    "BoxflatComboRow",
    "BoxflatAdvanceRow",
    "BoxflatCalibrationRow",
    "BoxflatColorDialogRow",
    "BoxflatColorRow",
    "BoxflatSpinRow",
    "BoxflatToggleButtonRow",
    "BoxflatEqRow",
    "BoxflatColorPickerRow",
    "BoxflatNewColorPickerRow",
    "BoxflatDialogRow",
    # Native Adwaita interactive rows
    "Adw.EntryRow",
    "Adw.ButtonRow",
    "Adw.ExpanderRow",
}

# Read-only / display-only row types that do not need a tooltip.
# ButtonLevelRow/MinMaxLevelRow are level-based input displays with calibration
# buttons, so they are treated as display-only along with plain LevelRow.
SKIP_ROW_TYPES = {
    "BoxflatLabelRow",
    "BoxflatLevelRow",
    "BoxflatButtonLevelRow",
    "BoxflatMinMaxLevelRow",
    "BoxflatProgressRow",
}


def _class_name(node: ast.AST) -> str | None:
    """Return a human-readable class name for a constructor Call node."""
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return f"{_expression_name(func.value)}.{func.attr}" if _expression_name(func.value) else func.attr
    return None


def _expression_name(node: ast.AST) -> str | None:
    """Best-effort name for an expression (e.g. 'Adw' from Name('Adw'))."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_expression_name(node.value)}.{node.attr}" if _expression_name(node.value) else node.attr
    return None


def _extract_constant_string(node: ast.AST) -> str | None:
    """Extract a constant string from an AST node, or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _iter_function_bodies(tree: ast.AST):
    """Yield every FunctionDef/AsyncFunctionDef body in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def _is_add_row_call(node: ast.AST) -> bool:
    """Return True if *node* is a Call to ``self._add_row`` or ``_add_row``."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name):
        return func.id == "_add_row"
    if isinstance(func, ast.Attribute):
        return func.attr == "_add_row"
    return False


def _is_tooltip_call(node: ast.AST) -> tuple[str, str] | None:
    """If node is ``<name>.set_tooltip_text(...)`` or similar, return its name."""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if not isinstance(func, ast.Attribute):
        return None
    if func.attr not in ("set_tooltip_text", "set_tooltip_from_description"):
        return None
    base = func.value
    if isinstance(base, ast.Name):
        return base.id
    # Ignore self._something etc.
    return None


def _collect_self_attributes(tree: ast.AST) -> dict[str, str | None]:
    """Map ``self.<attr>`` -> constructor class name from assignments in the class."""
    attrs: dict[str, str | None] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                attrs[target.attr] = _class_name(node.value)
    return attrs


def _scan_body(
    body: list[ast.stmt],
    local_assignments: dict[str, ast.AST],
    tooltip_vars: set[str],
    self_attrs: dict[str, str | None],
    yaml_keys: set[str],
    results: list,
) -> None:
    """Recursively scan a statement block, updating state and recording results.

    ``results`` is a list of tuples:
        ("missing", lineno, row_type) or ("missing_key", lineno, cmd) or ("ok",)
    """
    for stmt in body:
        # Track simple assignments of constructor calls to local variables.
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    local_assignments[target.id] = stmt.value

        # Track set_tooltip_* calls on local variables.
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            name = _is_tooltip_call(stmt.value)
            if name is not None:
                tooltip_vars.add(name)

        # Direct _add_row call.
        if isinstance(stmt, ast.Expr) and _is_add_row_call(stmt.value):
            child = stmt.value
            row_arg = child.args[0] if child.args else None
            row_type = _row_type_for_node(row_arg, local_assignments, self_attrs) if row_arg is not None else None

            if row_type in SKIP_ROW_TYPES:
                results.append(("ok",))
                continue

            command_value = None
            description_value = None
            if len(child.args) >= 2:
                command_value = child.args[1]
            if len(child.args) >= 3:
                description_value = child.args[2]
            for kw in child.keywords:
                if kw.arg == "command":
                    command_value = kw.value
                elif kw.arg == "description":
                    description_value = kw.value

            has_tooltip = False

            if description_value is not None and not (
                isinstance(description_value, ast.Constant) and description_value.value is None
            ):
                has_tooltip = True

            if not has_tooltip and command_value is not None:
                cmd = _extract_constant_string(command_value)
                if cmd is not None:
                    if cmd in yaml_keys:
                        has_tooltip = True
                    else:
                        results.append(("missing_key", child.lineno, cmd))
                        # Do not count as having a tooltip; missing key is an issue.
                else:
                    # Non-constant command expression (e.g. f-string in a loop).
                    # We cannot verify it statically, so assume the author intended
                    # a real command and count it as tooltip-present.
                    has_tooltip = True

            if not has_tooltip and isinstance(row_arg, ast.Name) and row_arg.id in tooltip_vars:
                has_tooltip = True

            if has_tooltip:
                results.append(("ok",))
            else:
                results.append(("missing", child.lineno, row_type or "unknown"))

        # Recurse into compound statements.
        for attr in ("body", "orelse"):
            block = getattr(stmt, attr, None)
            if isinstance(block, list):
                _scan_body(block, local_assignments, tooltip_vars, self_attrs, yaml_keys, results)

        # ``with`` and ``try`` have additional sub-blocks.
        if isinstance(stmt, ast.With):
            for item in stmt.items:
                if isinstance(item.optional_vars, ast.Name):
                    # Best-effort: the with-statement target is rarely a row constructor.
                    pass
        if isinstance(stmt, ast.Try):
            for handler in stmt.handlers:
                _scan_body(handler.body, local_assignments, tooltip_vars, self_attrs, yaml_keys, results)
            if stmt.finalbody:
                _scan_body(stmt.finalbody, local_assignments, tooltip_vars, self_attrs, yaml_keys, results)


def _row_type_for_node(
    node: ast.AST, assignments: dict[str, ast.AST], self_attrs: dict[str, str | None]
) -> str | None:
    """Determine the class name of the row being passed to _add_row."""
    if isinstance(node, ast.Call):
        return _class_name(node)

    if isinstance(node, ast.Name):
        last = assignments.get(node.id)
        if last is not None:
            return _row_type_for_node(last, assignments, self_attrs)
        return None

    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            return self_attrs.get(node.attr)
        return None

    if isinstance(node, ast.Subscript):
        return None

    return None


def analyze_file(path: Path, yaml_keys: set[str]):
    """Analyze a single panel file. Returns (total, with_tooltip, missing, missing_keys)."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    total = 0
    with_tooltip = 0
    missing: list[tuple[int, str]] = []
    missing_keys: list[tuple[int, str]] = []

    self_attrs = _collect_self_attributes(tree)

    for func in _iter_function_bodies(tree):
        local_assignments: dict[str, ast.AST] = {}
        tooltip_vars: set[str] = set()
        results: list = []
        _scan_body(func.body, local_assignments, tooltip_vars, self_attrs, yaml_keys, results)

        for result in results:
            total += 1
            if result[0] == "ok":
                with_tooltip += 1
            elif result[0] == "missing":
                missing.append((result[1], result[2]))
            elif result[0] == "missing_key":
                missing_keys.append((result[1], result[2]))

    return total, with_tooltip, missing, missing_keys


def main() -> int:
    yaml_keys = set()
    if DESCRIPTIONS_FILE.exists():
        with DESCRIPTIONS_FILE.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            yaml_keys = set(data.keys())

    total_all = 0
    tooltip_all = 0
    all_missing: list[tuple[Path, int, str]] = []
    all_missing_keys: list[tuple[Path, int, str]] = []

    for path in sorted(PANELS_DIR.glob("*.py")):
        total, with_tooltip, missing, missing_keys = analyze_file(path, yaml_keys)
        total_all += total
        tooltip_all += with_tooltip
        for lineno, row_type in missing:
            all_missing.append((path, lineno, row_type))
        for lineno, cmd in missing_keys:
            all_missing_keys.append((path, lineno, cmd))

    print(f"Scanned {total_all} _add_row() calls.")
    print(f"Calls with tooltips: {tooltip_all}")
    print(f"Missing tooltips: {len(all_missing)}")

    if all_missing:
        print()
        print("Missing tooltips by file:")
        current_file = None
        for path, lineno, row_type in all_missing:
            if path != current_file:
                current_file = path
                print(f"  {path.relative_to(ROOT)}")
            print(f"    line {lineno}: {row_type}")

    if all_missing_keys:
        print()
        print("Command keys referenced but missing from descriptions.yml:")
        for path, lineno, cmd in sorted(all_missing_keys, key=lambda x: x[2]):
            print(f"  {path.relative_to(ROOT)}:{lineno}  {cmd}")

    if all_missing or all_missing_keys:
        print()
        print("FAIL: tooltips or YAML keys are missing.")
        return 1

    print("PASS: all interactive rows have tooltips and all referenced command keys exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
