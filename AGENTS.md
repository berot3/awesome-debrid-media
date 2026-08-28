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
3. Update `verified_at` for claims that were actually rechecked; do not refresh dates mechanically.
4. Run:

```bash
python3 scripts/validate.py
python3 scripts/build.py
```

5. Review generated output for factual and presentation regressions.

## Scope controls

Do not:

- add standalone streaming clients to the primary comparison unless they are necessary as context;
- rank projects by stars;
- label projects `safe`, `legal`, `best`, or `recommended` without an explicit methodology that supports such a claim;
- treat inclusion as endorsement;
- weaken evidence requirements for convenience;
- add analytics, tracking, advertising, or accounts to the static site;
- add a heavy frontend framework without a demonstrated need.

## Review principle

When uncertain, preserve uncertainty in the data. `unconfirmed` is preferable to a confident but unsupported yes/no claim.
