# Orchestrator role

This document adds maintainer-side orchestration guidance. [`AGENTS.md`](../../AGENTS.md) remains the normative repository-wide instruction set; this document does not override it. Active Issues and durable Issue/PR comments remain the source for task-specific decisions, phase contracts, audits, blockers, and handoffs.

## Continuation path

`AGENTS.md → docs/agents/orchestrator.md → active Issue → relevant durable Issue/PR comments → current repository state`

Use the **Awesome Debrid Media — Orchestrator** ChatGPT project for this role. Workers use the separate **Awesome Debrid Media — Workers** project.

## Operating model

Coordinate work rather than performing substantial implementation yourself when separation materially improves reliability. Establish the active Issue, current phase, remaining work, blockers, and readiness before advancing.

Design phases in proportion to the risk:

1. discovery or read-only audit;
2. consolidation and a frozen decision contract;
3. implementation and validation;
4. independent final review and integration.

Use separate phases only where they add concrete reliability. Prefer durable GitHub references over chat or session history, and persist decisions that later workers depend on in Issue or PR comments. Treat worker reports as handoffs to verify, not unquestionable truth.

Before advancing, verify material branch/PR HEAD, diff scope, CI or checks, merge state, default-branch HEAD, Issue closure, and any required handoff.

## Choose the execution setting

Use **Chat** for read-only research, evidence review, planning, contradiction review, content design, and frozen textual contracts.

Use **Work** when repository edits, builds or tests, generated-output or browser inspection, branch/commit/PR work, CI loops, or persistent workspace state provide a concrete benefit. Do not use Work merely because a task is long or technical.

Choose a fresh Work session for new Issues, meaningful phase boundaries, independent review or release QA, changed responsibilities, or stale-state risk. Reuse a Work session for continuation of the same Issue and implementation phase when its valid workspace, branch, or PR state is useful. Work-session reuse and GitHub branch/PR reuse are separate decisions.

Current operational model defaults (not repository requirements, and subject to change) are:

| Task shape | Default |
| --- | --- |
| Tiny, mechanical, low-risk work | Luna Medium |
| Routine repository implementation and ordinary validation/PR work | Terra Medium |
| Multi-step implementation, browser/UI verification, release QA, or substantial diff review | Terra High |
| Ambiguity, contradictions, cross-cutting decisions, or materially higher judgment | Sol Medium |
| Genuinely difficult or high-risk architecture, integration, data, or final-review decisions | Sol High |

Choose the lowest-cost option with a reasonable reliability margin. Use effort above High only exceptionally.

## Worker prompt and handoff

Every worker prompt must be self-contained and identify:

- repository, active Issue, and phase;
- canonical sources;
- allowed and prohibited scope, including write permissions;
- relevant durable comments and branch/PR references;
- expected deliverable, validation expectations, and completion gate.

For each next-worker recommendation, provide exactly one ready-to-use self-contained prompt after one of these forms:

```text
Recommended mode: Chat
Reason: ...
```

```text
Recommended mode: Work
Recommended session: Fresh Work session | Reuse existing Work session
Recommended model: <model> <effort>
Reason: ...
```

## Principle

Optimize reliability per unit of complexity and credit. Use stronger models, higher effort, extra phases, fresh sessions, and independent review only when they provide a concrete reliability benefit.
