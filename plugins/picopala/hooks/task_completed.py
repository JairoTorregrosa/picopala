#!/usr/bin/env python3
"""TaskCompleted hook: Tasks need review approval before completion.

Exit codes (per Claude Code hooks spec):
  0 = allow completion
  2 = block completion, feed stderr back to model
  1 = non-blocking error (gate fails open — avoided by catching all exceptions)
"""
import json
import re
import sys
from pathlib import Path


def sanitize_id(raw_id: str) -> str:
    """Replace unsafe characters to prevent path traversal."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", raw_id)


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

    safe_team = sanitize_id(team_name)
    safe_task = sanitize_id(task_id)

    state_dir = Path.home() / ".claude" / "picopala-state" / safe_team
    marker = state_dir / f"{safe_task}.approved"

    if marker.exists():
        sys.exit(0)

    print(
        f"Task '{task_subject}' ({task_id}) cannot be completed — "
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
