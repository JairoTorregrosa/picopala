# Plan Template

Use this template for `<topic>-plan.md` files.

```markdown
# [Topic] Plan

## Goal
[1-2 sentence description of what we're building]

## Constraints
- [Tech stack, patterns, risks]

## Config
- **max_review_rounds**: 2

## Tasks

### T1: [Task Name]
- **depends_on**: []
- **location**: [file paths]
- **description**: [what to implement]
- **acceptance_criteria**: [list of criteria]
- **validation**: [how to verify]
- **status**: pending
- **model**: [optional: sonnet/opus override for worker/reviewer]
- **log**:
- **files**:

### T2: [Task Name]
- **depends_on**: [T1]
- **location**: [file paths]
- **description**: [what to implement]
- **acceptance_criteria**: [list of criteria]
- **validation**: [how to verify]
- **status**: pending
- **log**:
- **files**:

## Dependency Graph
T1 → T2 → T3
     ↘ T4 ↗

## Parallel Execution Waves
| Wave | Tasks | Depends On |
|------|-------|------------|
| 1    | T1    | -          |
| 2    | T2, T3| T1         |
| 3    | T4    | T2, T3     |
```
