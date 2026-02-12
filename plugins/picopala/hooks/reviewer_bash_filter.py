#!/usr/bin/env python3
"""PreToolUse hook: Whitelist read-only Bash commands for picopala reviewers.

Only allows predefined verification commands. Blocks everything else.
This hook is defined in the picopala-reviewer agent frontmatter, so it
only activates when the reviewer agent is running.

Exit codes (per Claude Code hooks spec):
  0 = allow the tool call
  2 = block the tool call, feed stderr back to model
"""
import json
import re
import sys

# Exact command prefixes allowed for reviewers.
# These are read-only verification commands that cannot modify files.
ALLOWED_PREFIXES = [
    # Test & quality checks
    "bun run test",
    "bun run typecheck",
    "bun lint",
    "bun run build",
    "bun run quality",
    # Git read-only
    "git log",
    "git diff",
    "git show",
    "git rev-parse",
    "git status",
    "git branch",
    # Node/bun read-only
    "bunx convex codegen",
    "bun run test:run",
    "bun run test:coverage",
    "bun run quality:fast",
]

# Shell metacharacters that could chain/redirect commands
DANGEROUS_CHARS = re.compile(r"[;|&`$><]")


def is_allowed(command: str) -> bool:
    """Check if a command matches the whitelist."""
    cmd = command.strip()

    # Block shell metacharacters — prevents chaining (cmd1 && cmd2, cmd | rm, etc.)
    if DANGEROUS_CHARS.search(cmd):
        return False

    # Check against allowed prefixes
    return any(cmd.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("Reviewer bash filter: failed to parse input JSON.", file=sys.stderr)
        sys.exit(2)

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        print("Reviewer bash filter: empty command blocked.", file=sys.stderr)
        sys.exit(2)

    if is_allowed(command):
        sys.exit(0)

    print(
        f"Blocked: reviewers can only run read-only verification commands.\n"
        f"Attempted: {command}\n"
        f"Allowed commands: bun run test, bun run typecheck, bun lint, "
        f"bun run build, git log/diff/show/status",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Reviewer bash filter: unexpected error: {e}", file=sys.stderr)
        sys.exit(2)
