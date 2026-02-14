#!/usr/bin/env python3
"""TaskCompleted hook: Plan tasks need review approval before completion.

Only gates tasks whose subject matches the plan task naming convention
(e.g., "T1: Research", "T2: HTML Development"). Worker-internal subtasks
(created by workers to organize their own work) are allowed through
unconditionally to prevent deadlocks.

Exit codes (per Claude Code hooks spec):
  0 = allow completion
  2 = block completion, feed stderr back to model
  1 = non-blocking error (gate fails open — avoided by catching all exceptions)
"""
import json
import re
import sys
from pathlib import Path

# Pattern for plan tasks: "T1: ...", "T2: ...", etc.
PLAN_TASK_PATTERN = re.compile(r"^T\d+[:\s]")


def sanitize_id(raw_id: str) -> str:
    """Replace unsafe characters to prevent path traversal."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", raw_id)


def is_plan_task(subject: str) -> bool:
    """Check if a task subject matches the plan task naming convention."""
    return bool(PLAN_TASK_PATTERN.match(subject))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("TaskCompleted hook: failed to parse input JSON.", file=sys.stderr)
        sys.exit(2)

    team_name = data.get("team_name") or ""
    task_id = data.get("task_id") or ""
    task_subject = data.get("task_subject") or task_id

    # Only activate for picopala sessions
    if not team_name.startswith("picopala-"):
        sys.exit(0)

    # No task_id means implicit TaskCompleted event (teammate turn end).
    # Allow these — the gate only enforces explicit task completion.
    if not task_id:
        sys.exit(0)

    # Only gate plan tasks (T1, T2, T3, etc.). Worker-internal subtasks
    # are allowed through to prevent deadlocks where workers create their
    # own subtasks that then get blocked by missing approval markers.
    if not is_plan_task(task_subject):
        sys.exit(0)

    safe_team = sanitize_id(team_name)
    safe_task = sanitize_id(task_subject)

    state_dir = Path.home() / ".claude" / "picopala-state" / safe_team
    marker = state_dir / f"{safe_task}.approved"

    if marker.exists():
        sys.exit(0)

    print(
        f"Plan task '{task_subject}' ({task_id}) cannot be completed — "
        f"no review approval found.\n"
        f"The lead must write the approval marker after receiving "
        f"APPROVED verdict from the reviewer.\n"
        f"Run: mkdir -p {state_dir} && "
        f"echo APPROVED > {state_dir}/{safe_task}.approved",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"TaskCompleted hook: unexpected error: {e}", file=sys.stderr)
        sys.exit(2)
