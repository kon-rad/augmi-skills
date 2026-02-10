---
name: spec-interview
description: Interview me deeply (AskUserQuestionTool), then write back a complete spec.
---

Read the spec file at this path: $ARGUMENTS

Interview me using AskUserQuestionTool to gather Ralph-ready requirements:
- Concrete deliverables (not vague goals)
- Verification commands (test/lint/typecheck/build)
- Edge cases and constraints

Push back on vague answers. Keep interviewing until you have VERIFIABLE success criteria.

Write a concise spec using this structure:

```markdown
# [Title]

## Requirements
- [Specific requirement 1]
- [Specific requirement 2]

## Verification
- `pnpm test`
- `pnpm typecheck`
- [other project-specific commands]

## Success Criteria
- All verification commands pass
- [Specific measurable criteria]

## Ralph Command
/ralph-loop:ralph-loop "Read [SPEC_PATH] and implement requirements" --max-iterations 30 --completion-promise "All verification commands pass"
```

Adapt based on task type:
- **Feature**: List requirements, use --max-iterations 30
- **TDD**: List test cases instead of requirements, use --max-iterations 50
- **Bug fix**: Include repro steps + expected/actual, use --max-iterations 20
- **Refactor**: List goals + constraints, use --max-iterations 25

---

## Large projects only

If 6+ requirements or multi-system work, split into 2-5 sequential phases:

```markdown
# [Project Name]

## Verification (all phases)
- `pnpm test && pnpm typecheck`

---

## Spec 1: [Phase Name]
### Requirements
- [...]
### Success Criteria
- All verification commands pass
### Ralph Command
/ralph-loop:ralph-loop "Read [SPEC_PATH], implement Spec 1" --max-iterations 25 --completion-promise "All verification commands pass"

(repeat pattern for each phase, adding Prerequisites for Spec 2+)
```

Phase order: setup → core features → polish/cleanup. Each phase must leave codebase working.