# Execution Summary Template

Use this template after all waves complete to report results.

```markdown
# Execution Summary

## Tasks: [N] total | [done] completed | [failed] failed | [issues] review findings

### Wave [N]
| Task | Worker | Reviewer | Rounds | Verdict | Findings |
|------|--------|----------|--------|---------|----------|
| T1 | worker-t1 | reviewer-t2 | 1 | APPROVED | 0 |
| T2 | worker-t2 | reviewer-t1 | 2 | APPROVED | 3 (2 fixed) |
| T3 | worker-t3 | reviewer-t3 | 2 | FAILED | 4 (too complex) |

### Cross-Review Stats
- Reviewed: [N] | First-pass APPROVED: [N] | Required revision: [N] | Failed (max rounds): [N]
- Total review rounds: [N] | Avg rounds per task: [N]

### Issues Caught by Reviewers
- T2 R1: [Issue found by reviewer] → [Fix applied in R1]
- T2 R2: [Re-review confirmed fix] → APPROVED

### Failed Tasks (exceeded review budget)
- T3: [reason — suggest decomposition]

## Files Modified
[list of all files changed across all waves]

## Team Composition
- Lead: [you]
- Workers: [list]
- Fixers: [list, if any review rounds required revision]
- Reviewers: [list] (fresh per round)
```
