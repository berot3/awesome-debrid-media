# Worker role

This document adds execution-side guidance. [`AGENTS.md`](../../AGENTS.md) remains the normative repository-wide instruction set; this document does not override it. Active Issues and durable Issue/PR comments hold task-specific decisions, phase contracts, audits, blockers, and handoffs.

## Continuation path

`AGENTS.md → docs/agents/worker.md → active Issue → relevant durable Issue/PR comments → current repository state`

Read in that order. GitHub and repository state are canonical, not previous chat or session history.

## Execute the assigned phase

- Follow the active Issue and assigned phase strictly, including its allowed/prohibited scope and explicit read-only or write permissions.
- Do not opportunistically implement adjacent Issues.
- When supplied an existing task branch or PR, verify its current GitHub state and reuse it if still valid.
- Run task-relevant validation, then review the complete diff against the current base branch and remove unrelated cleanup.
- Leave the required durable Issue/PR handoff when later work depends on the result.
- Report branch, PR, commit, and CI/check state accurately.
- Stop at the defined completion gate; do not invent the next phase.
