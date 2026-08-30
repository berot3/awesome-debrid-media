# Methodology

Awesome Debrid Media aims to make compatibility claims traceable rather than merely plausible.

## Evidence hierarchy

For manually curated claims, prefer sources in this order:

1. official project documentation;
2. repository source code;
3. official README;
4. official issues, pull requests, and releases;
5. direct maintainer statements;
6. community sources as secondary context.

When current first-party documentation conflicts with older third-party material, current first-party documentation wins unless there is strong evidence that the documentation is stale.

## What "confirmed" means

A claim is confirmed when the cited evidence directly supports the specific classification being made.

Examples:

- A README naming AIOStreams supports `explicit`.
- Generic Stremio-addon code plus first-party evidence that configured Stremio addons are accepted may support `stremio_protocol`; do not promote it to `explicit` without AIOStreams-specific evidence.
- A maintainer permanently excluding remote URL streaming may support `scope_conflict` when that capability is necessary for the integration under discussion.

## Absence is not evidence

Repository search is useful for discovery but a zero-result search does not prove lack of support.

If the project is relevant and no conclusive evidence is found, use `unconfirmed` rather than `none`.

Use `none` only when a durable source supports an unsupported/absent conclusion. Use `scope_conflict` only when product direction or permanent non-goals provide stronger evidence.

## AIOStreams vs. Stremio protocol

AIOStreams compatibility is not a single implementation path.

The dataset therefore separates:

- explicit AIOStreams integration;
- generic Stremio-addon compatibility;
- plugin/bridge paths;
- uncertainty;
- explicit lack of first-party support;
- documented scope conflicts.

This avoids both undercounting generic-protocol solutions and overstating them as bespoke AIOStreams integrations.

## Apple TV/tvOS

Apple-platform claims distinguish source code from a usable release.

A tvOS target or React Native TV configuration proves that a code path exists. It does not prove that a user can currently install a supported public build.

Where possible, evidence should identify the distribution path, such as App Store, TestFlight, GitHub release/IPA, or source-only Xcode build.

## Freshness

Each project has a `verified_at` date representing the latest meaningful manual verification of the curated record. Each evidence entry has a `checked_at` date representing when that specific source/claim was actually revisited.

Do not update either date merely because a file was reformatted, GitHub metadata changed, or a different source was reviewed. Do not mechanically set `verified_at` to the newest evidence date.

The default re-audit reminder threshold is **120 days**. A project record or evidence entry at least 120 days old is considered **due for recheck**.

Freshness is advisory only. Age does not prove that a claim is incorrect, unsupported, `none`, `no`, or `unconfirmed`, and stale items do not fail normal validation or the site build.

v0.3 intentionally uses one threshold for all curated claims. Different freshness windows for volatile release/client paths versus slower-moving architectural facts may be considered later if maintenance experience justifies the additional policy complexity.

Use `python3 scripts/freshness.py` for the maintainer-facing report. See `docs/freshness.md` for the deterministic `--as-of` workflow, JSON output, and the complete re-audit procedure.

## Dynamic GitHub metadata

Stars, forks, last push, archival state, and similar repository metadata are volatile. They are not manually stored in `data/projects.json`.

The site build may enrich curated records with current public GitHub metadata. If enrichment fails, the curated dataset must remain valid and the build should degrade gracefully.

GitHub stars are displayed only as context. They are not a quality, safety, maturity, or recommendation score.

## Inclusion policy

Inclusion means a project is useful to compare in this ecosystem. It does not mean the maintainers of Awesome Debrid Media endorse it.

A project may be included even when it has no first-party AIOStreams support, provided its architecture makes the comparison useful. Such records must be labeled accurately.

Standalone streaming clients are outside the primary comparison unless they are required to explain a server-side client path.

## Corrections

When evidence changes, prefer correcting the structured record and preserving the evidence trail rather than defending an older classification.
