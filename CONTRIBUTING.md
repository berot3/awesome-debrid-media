# Contributing

Contributions are welcome when they improve the accuracy or coverage of the comparison.

## Useful contributions

Examples:

- add a relevant self-hosted media server, backend, bridge, VFS, or plugin;
- provide first-party evidence that a project's AIOStreams status changed;
- correct Apple TV/tvOS availability;
- update Debrid/Usenet/provider support with official evidence;
- correct architecture or dependency classification;
- improve the static site without duplicating project facts outside the dataset.

## Evidence first

Please provide a durable source where possible. Preferred sources are:

1. official documentation;
2. repository source code;
3. official README;
4. official issue, pull request, or release;
5. direct maintainer statement;
6. community source as secondary context.

A missing search result is not evidence that a feature is unsupported.

## Editing project data

Curated facts live in `data/projects.json`. See:

- `docs/definitions.md`
- `docs/methodology.md`
- `docs/schema.md`

Before submitting a change, run:

```bash
python3 scripts/validate.py
python3 scripts/build.py
```

## Inclusion is not endorsement

Projects may be listed because they are architecturally relevant even when they do not support AIOStreams. A project with `none` or `scope_conflict` status is still useful comparison data.

GitHub stars and activity are informational metadata, not a ranking or recommendation score.
