# Changelog

## 0.2.0

Post-mortem fixes from first production run (magic-nails, 3 tasks / 3 workers / 3 reviewers).

### Bug Fixes

- **Worker hook cycling** (HIGH): Workers called `TaskUpdate` despite text instructions, triggering the `task_completed.py` hook which blocked them (no `.approved` marker yet). Workers entered confused retry loops. Fixed by adding `TaskUpdate`, `TaskCreate`, `TaskList` to `disallowedTools` in worker agent frontmatter — structural prevention, not just instructions.
- **`rm -rf` blocked by security hooks** (LOW): Phase 6 cleanup used `rm -rf ~/.claude/picopala-state/...` which project-level security hooks block. Replaced with safer `rm *.approved; rmdir` pattern.
- **Missing execution summary** (LOW): Phase 6 said "display summary" but didn't enforce it. Changed to "You MUST render the execution summary before finishing."
- **`task_completed.py` subtask deadlocks**: Hook now only gates plan tasks (`T1:`, `T2:`, etc.) and passes worker-internal subtasks unconditionally. Uses `task_subject` for marker filenames instead of `task_id`.

### Improvements

- **Pre-flight check**: Distinguishes tracked vs untracked files — untracked files no longer block team creation since they don't cause merge conflicts.
- **Model selection guidance**: Plan phase now recommends `model: sonnet` for trivial tasks to reduce cost, reserving `opus` for complex logic.
- **Review round trade-offs**: Intake phase explains consequences of 1/2/3 max review rounds so users make informed choices.
- **Worker validation mandatory**: Changed from "run validation if feasible" to mandatory — workers must run typecheck/lint/tests and fix errors before committing.
- **i18n namespace scoping**: Worker prompts now include namespace boundaries when tasks touch translation files.
- **Stop hook false positive docs**: Added note that project-level quality hooks may report errors from workers' in-progress code during parallel execution — expected noise, ignore until wave completes.

## 0.1.0

- Initial release: Picopala — Agents Checking Agents
