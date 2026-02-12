#!/usr/bin/env python3
"""
picopala.py — CLI helper for Picopala multi-agent orchestration plans.

Commands:
  validate <plan-file>  Validate plan structure and dependencies
  waves <plan-file>     Output parallel execution waves as JSON
  status <plan-file>    Show task completion status summary

Designed to fail loudly on malformed input. No external dependencies.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def parse_plan(path: str) -> list[dict]:
    """Parse a plan markdown file into a list of task dicts."""
    text = Path(path).read_text()
    task_pattern = re.compile(
        r"^###\s+(T[\d.]+):\s*(.+)$", re.MULTILINE
    )
    field_pattern = re.compile(
        r"^-\s+\*\*(\w+(?:_\w+)*)\*\*:\s*(.+)$", re.MULTILINE
    )

    tasks = []
    matches = list(task_pattern.finditer(text))

    if not matches:
        raise ValueError(
            f"No tasks found in {path}. "
            "Tasks must be formatted as '### T1: Task Name'"
        )

    for i, match in enumerate(matches):
        task_id = match.group(1)
        task_name = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end]

        fields = {}
        for fm in field_pattern.finditer(section):
            key = fm.group(1)
            value = fm.group(2).strip()
            fields[key] = value

        # Parse depends_on as list
        deps_raw = fields.get("depends_on", "[]")
        deps_match = re.findall(r"T[\d.]+", deps_raw)
        fields["depends_on"] = deps_match

        tasks.append({
            "id": task_id,
            "name": task_name,
            **fields,
        })

    return tasks


def validate(tasks: list[dict], path: str) -> list[str]:
    """Validate plan structure. Returns list of errors (empty = valid)."""
    errors = []
    task_ids = {t["id"] for t in tasks}
    required_fields = ["depends_on", "location", "description", "acceptance_criteria", "validation", "status"]
    valid_statuses = {"pending", "in_progress", "completed", "failed"}

    for task in tasks:
        tid = task["id"]

        # Check required fields
        for field in required_fields:
            if field not in task or (task[field] is None or (isinstance(task[field], str) and not task[field])):
                errors.append(f"{tid}: missing required field '{field}'")

        # Check status enum
        status = task.get("status", "").lower()
        if status and status not in valid_statuses:
            errors.append(f"{tid}: invalid status '{status}'. Must be one of: {sorted(valid_statuses)}")

        # Check dependency references exist
        for dep in task.get("depends_on", []):
            if dep not in task_ids:
                errors.append(
                    f"{tid}: depends on '{dep}' which does not exist. "
                    f"Available: {sorted(task_ids)}"
                )

    # Check for circular dependencies
    visited = set()
    rec_stack = set()
    adj = defaultdict(list)
    for task in tasks:
        for dep in task.get("depends_on", []):
            adj[dep].append(task["id"])

    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in adj[node]:
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                errors.append(
                    f"Circular dependency detected involving '{node}' -> '{neighbor}'"
                )
                return True
        rec_stack.discard(node)
        return False

    for tid in task_ids:
        if tid not in visited:
            has_cycle(tid)

    return errors


def compute_waves(tasks: list[dict]) -> list[list[str]]:
    """Compute parallel execution waves from task dependencies."""
    task_map = {t["id"]: t for t in tasks}
    completed = set()
    remaining = set(task_map.keys())
    waves = []

    # Filter out already completed tasks
    for t in tasks:
        if t.get("status", "").lower() == "completed":
            completed.add(t["id"])
            remaining.discard(t["id"])

    max_iterations = len(tasks) + 1
    iteration = 0

    while remaining:
        wave = []
        for tid in sorted(remaining):
            deps = set(task_map[tid].get("depends_on", []))
            if deps.issubset(completed):
                wave.append(tid)

        if not wave:
            raise ValueError(
                f"Deadlock: tasks {sorted(remaining)} have unsatisfied "
                f"dependencies. Completed: {sorted(completed)}"
            )

        waves.append(wave)
        completed.update(wave)
        remaining -= set(wave)

        iteration += 1
        if iteration > max_iterations:
            raise ValueError("Wave computation exceeded maximum iterations")

    return waves


def cmd_validate(path: str):
    """Validate command."""
    tasks = parse_plan(path)
    errors = validate(tasks, path)

    if errors:
        print(f"VALIDATION FAILED — {len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"VALID — {len(tasks)} tasks, all dependencies resolved.")
    for t in tasks:
        deps = t.get("depends_on", [])
        print(f"  {t['id']}: {t['name']} (depends_on: {deps})")


def cmd_waves(path: str):
    """Waves command — output as JSON."""
    tasks = parse_plan(path)
    errors = validate(tasks, path)
    if errors:
        print("Plan has validation errors. Fix them first:", file=sys.stderr)
        for e in errors:
            print(f"  ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    waves = compute_waves(tasks)
    output = []
    for i, wave in enumerate(waves, 1):
        task_details = []
        task_map = {t["id"]: t for t in tasks}
        for tid in wave:
            task_details.append({
                "id": tid,
                "name": task_map[tid]["name"],
                "depends_on": task_map[tid].get("depends_on", []),
            })
        output.append({"wave": i, "tasks": task_details})

    print(json.dumps(output, indent=2))


def cmd_status(path: str):
    """Status command — show completion summary."""
    tasks = parse_plan(path)
    total = len(tasks)
    by_status = defaultdict(list)

    for t in tasks:
        status = t.get("status", "unknown").lower()
        by_status[status].append(t["id"])

    completed = len(by_status.get("completed", []))
    pending = len(by_status.get("pending", []))
    in_progress = len(by_status.get("in_progress", []))
    failed = len(by_status.get("failed", []))

    print(f"Plan: {path}")
    print(f"Total: {total} | Completed: {completed} | In Progress: {in_progress} | Pending: {pending} | Failed: {failed}")
    print()

    for status, tids in sorted(by_status.items()):
        print(f"  [{status}]: {', '.join(sorted(tids))}")


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        print("Usage: picopala.py <command> <plan-file>", file=sys.stderr)
        print("Commands: validate, waves, status", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    path = sys.argv[2]

    if not Path(path).exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    commands = {
        "validate": cmd_validate,
        "waves": cmd_waves,
        "status": cmd_status,
    }

    if command not in commands:
        print(f"ERROR: Unknown command '{command}'. Use: {', '.join(commands)}", file=sys.stderr)
        sys.exit(1)

    commands[command](path)


if __name__ == "__main__":
    main()
