# AGENTS.md

This repository is curated, evidence-based reference material first and a static website second.

## Source of truth

- `data/projects.json` is the factual source of truth for manually curated project information.
- Generated output in `dist/` must never be edited directly.
- Do not duplicate manually curated facts into separate HTML, Markdown, or JavaScript data structures.
- Volatile GitHub metadata such as stars, forks, last push, release activity, and archival status is not manually curated.

## Evidence rules

- Load-bearing compatibility claims require evidence.
- Prefer evidence in this order: official docs, source code, README, official issues/PRs/releases, direct maintainer statements, then community sources.
- Do not convert `not found` into `not supported`.
- Distinguish `unconfirmed` from `none`.
- Distinguish `none` from `scope_conflict`.
- A project saying it supports Debrid is not evidence that it supports AIOStreams.
- Generic Stremio-addon support is not automatically `explicit` AIOStreams support.
- A codebase containing tvOS support is not proof that an installable public Apple TV release exists.
- Never infer one Riven implementation's features from another. Riven TS, Riven RS, and legacy Riven are separate projects with separate evidence.
- Evidence age is a maintenance signal only. A stale `checked_at` or `verified_at` date never proves that the underlying claim is false or unsupported.

## AIOStreams states

Allowed values are:

- `explicit`
- `stremio_protocol`
- `plugin_or_bridge`
- `unconfirmed`
- `none`
- `scope_conflict`

Any state other than `unconfirmed` requires at least one evidence entry supporting that classification.

## Architecture states

Use the narrowest accurate architecture classification:

- `full_media_server`
- `streaming_backend`
- `jellyfin_compatible_server`
- `bridge`
- `media_automation_vfs`
- `media_server_plugin`
- `other`

Do not force every project into the label "media server".

## Editing workflow

Before changing project data:

1. Read `docs/definitions.md`, `docs/methodology.md`, and `docs/schema.md`.
2. Verify claims using current first-party sources whenever possible.
3. Update an evidence entry's `checked_at` only when that specific source/claim was actually rechecked. Update project-level `verified_at` only after a meaningful record-level manual verification; do not refresh either date mechanically.
4. Run:

```bash
python3 scripts/validate.py
python3 scripts/build.py
```

5. Review generated output for factual and presentation regressions.

## Freshness / re-audit workflow

- The default advisory re-audit threshold is 120 days.
- Run `python3 scripts/freshness.py` to list project records and evidence entries due for recheck.
- For reproducible agent work, use an explicit date such as `python3 scripts/freshness.py --as-of YYYY-MM-DD`.
- Stale items are `needs recheck`, not `incorrect`, `unsupported`, `none`, `no`, or `unconfirmed`.
- The freshness report is advisory and must not be turned into a build failure merely because items are old.
- Follow `docs/freshness.md` for the complete re-audit procedure and date semantics.

## Evidence link health

- Run `python3 scripts/check_evidence_links.py` to inspect stored evidence URLs.
- A redirect, 404/410, access/rate-limit response, timeout, or network failure is a citation-maintenance signal only. It never proves that the underlying project claim is false or unsupported.
- Never change capability states, evidence entries, `checked_at`, or `verified_at` automatically from link-check output.
- Manually re-open or replace the source and re-verify the claim before editing evidence or dates.
- Follow `docs/evidence-links.md` for result categories and the remediation procedure.

## Scope controls

Do not:

- add standalone streaming clients to the primary comparison unless they are necessary as context;
- rank projects by stars;
- label projects `safe`, `legal`, `best`, or `recommended` without an explicit methodology that supports such a claim;
- treat inclusion as endorsement;
- weaken evidence requirements for convenience;
- add analytics, tracking, advertising, or accounts to the static site;
- add a heavy frontend framework without a demonstrated need.

## Agent handoffs and task scope

Repository and GitHub state are canonical for agent work.

- Do not depend on previous chat or session history when the relevant state can be read from the repository, the active GitHub Issue, Issue/PR comments, branches, commits, or pull requests.
- A later agent should be able to continue from `AGENTS.md`, the active Issue, relevant durable Issue/PR comments, and current repository state.
- Use GitHub Issue or PR comments for issue-specific decision logs, audit results, and implementation handoffs when later agents need them. Do not create permanent repository spec files solely to preserve temporary orchestration state.
- Follow the active Issue and assigned phase strictly. Do not opportunistically implement adjacent Issues.
- If a task or phase is explicitly read-only, perform no repository or GitHub writes.
- If a task defines a completion gate or instructs the agent to stop after a phase, stop there.
- Reuse an existing task branch or pull request when it remains valid rather than creating competing replacements without a concrete reason.
- Treat reported branch heads, CI results, merge state, and Issue closure as claims to verify against GitHub before relying on them.
- After implementation, review the complete diff against the current base branch and ensure unrelated cleanup has not entered the task.

## Review principle

When uncertain, preserve uncertainty in the data. `unconfirmed` is preferable to a confident but unsupported yes/no claim.
