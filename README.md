# Picopala — Agents Checking Agents

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin for multi-agent orchestration with cross-validation. Every agent's work is reviewed by a different agent in an iterative adversarial loop.

## Install

1. Add the marketplace:

```
/plugin marketplace add JairoTorregrosa/picopala
```

2. Install the plugin:

```
/plugin install picopala@picopala
```

Or load locally for development:

```bash
claude --plugin-dir /path/to/picopala
```

## Usage

```
/picopala Build a REST API with auth, CRUD endpoints, and tests
```

The plugin orchestrates the full lifecycle:

```
Intake → Plan → Create Team → [Execute Wave → Cross-Review Loop] → Cleanup
```

## How It Works

```
      ┌──────────────────────────────────────────────┐
      │         TECH LEAD (delegate mode only)        │
      │   Coordinates, delegates, synthesizes.        │
      │   NEVER implements, edits files, or builds.   │
      └───┬──────────────┬──────────────┬────────────┘
          │              │              │
   ┌──────▼──┐    ┌──────▼──┐    ┌──────▼──┐
   │Worker A │    │Worker B │    │Worker C │    IMPLEMENT
   │implement│    │implement│    │implement│
   │  commit │    │  commit │    │  commit │
   └────┬────┘    └────┬────┘    └────┬────┘
        ✕              ✕              ✕         SHUTDOWN workers
        │              │              │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │Review B │    │Review C │    │Review A │    CROSS-REVIEW
   │→ REVISE │    │→APPROVE │    │→ REVISE │
   └────┬────┘    └─────────┘    └────┬────┘
        ✕                             ✕         SHUTDOWN reviewers
        │                             │
   ┌────▼────┐                   ┌────▼────┐
   │Fixer A  │                   │Fixer C  │    FIX (fresh agents)
   └────┬────┘                   └────┬────┘
        ✕                             ✕
   ┌────▼────┐                   ┌────▼────┐
   │Review B'│                   │Review A'│    RE-REVIEW
   │→APPROVE │                   │→APPROVE │    (fresh context)
   └─────────┘                   └─────────┘
```

**Key principles:**
- Fresh agents for each phase — no context pollution across rounds
- Reviewers are read-only (cannot edit files) with whitelisted Bash commands
- Tasks need reviewer APPROVED verdict before they can be marked complete (enforced by hook)
- Iterative convergence: fix-review cycles until APPROVED or budget exhausted

## Components

| Component | Description |
|-----------|-------------|
| **Skill** `picopala` | Orchestration pipeline (intake, plan, execute, cross-review, cleanup) |
| **Agent** `picopala-worker` | Implements tasks or applies review fixes, commits, reports to lead |
| **Agent** `picopala-reviewer` | Cross-reviews work, sends structured APPROVED/REVISE findings (read-only) |
| **Hook** `TaskCompleted` | Blocks task completion without review approval marker |
| **Hook** `PreToolUse(Bash)` | Whitelists read-only commands for reviewers |
| **Script** `picopala.py` | Plan validator CLI (validate, waves, status) |

## Requirements

- Claude Code 1.0.33+
- Python 3.10+ (for hook scripts)

## License

MIT
