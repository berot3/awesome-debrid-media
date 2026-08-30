# Evidence freshness and re-audit policy

Awesome Debrid Media treats evidence age as a **maintenance signal**, not as a factual contradiction.

An old `verified_at` or `checked_at` date means **needs recheck**. It does not mean that a project is unsupported, that a capability should become `no`/`none`, or that an existing classification should become `unconfirmed`.

## Default threshold

The default re-audit reminder threshold is **120 days**.

A project record or evidence entry is due when its date is 120 days old or older relative to the report's `as-of` date.

v0.3 intentionally uses one threshold for all curated claims. Client availability and release paths may be more volatile than architectural facts, but separate thresholds would add policy complexity before we have enough maintenance history to justify it. Revisit differentiated thresholds only after the report has been used in practice.

## Advisory-only behavior

Freshness is deliberately non-blocking:

- stale records do not fail the normal validator;
- stale records do not fail the site build;
- the freshness tool exits successfully when it finds due items;
- no project fact or verification date is changed automatically.

A non-zero exit from the freshness tool means the report itself could not be produced, for example because the data file or a date is invalid. It does **not** mean that evidence is merely old.

## Dates and their meaning

### `checked_at`

An evidence entry's `checked_at` date means that the cited source was actually revisited and the specific cited claim was checked against it on that date.

Do not refresh `checked_at` because another source was reviewed, because a file was reformatted, or because a nearby project field changed.

### `verified_at`

A project's `verified_at` date means that the curated project record received a meaningful record-level manual verification.

Do not mechanically set `verified_at` to the newest evidence date. Update it only when the project record was reviewed broadly enough that the date honestly represents a meaningful verification of the record.

## Freshness report

Run the maintainer-facing report with:

```bash
python3 scripts/freshness.py
```

For a reproducible report, pass an explicit date:

```bash
python3 scripts/freshness.py --as-of 2026-08-30
```

Machine-readable output is available for agents and other tooling:

```bash
python3 scripts/freshness.py --as-of 2026-08-30 --format json
```

The threshold can be overridden for investigation without changing repository policy:

```bash
python3 scripts/freshness.py --threshold-days 90
```

The report lists enough context to re-audit an item:

- project name and id;
- whether the stale date is project-level verification or an evidence entry;
- structured evidence path;
- date and age;
- evidence claim and URL where applicable.

## Re-audit workflow for agents and maintainers

When the report lists due items:

1. Run `python3 scripts/validate.py` first so freshness work starts from structurally valid data.
2. Run `python3 scripts/freshness.py --as-of YYYY-MM-DD` with an explicit current date and capture the due list.
3. Work project-by-project. Read `docs/definitions.md`, `docs/methodology.md`, and the existing project record before changing classifications.
4. Revisit current first-party sources whenever possible. Do not infer support from repository-search absence.
5. For each evidence source actually rechecked, update that evidence entry's `checked_at` and correct its claim/classification only if the current source justifies a change.
6. Update project-level `verified_at` only after a meaningful record-level review, not merely because one evidence URL was opened.
7. Preserve uncertainty. Old evidence by itself never justifies converting a state to `none`, `no`, `scope_conflict`, or `unconfirmed`.
8. Run:

   ```bash
   python3 scripts/validate.py
   python3 scripts/build.py
   python3 scripts/freshness.py --as-of YYYY-MM-DD
   ```

9. Review the remaining due list. It is valid for unrelated old evidence to remain due if it was not actually rechecked.

## Scheduled report

The repository also runs an advisory evidence-freshness workflow weekly and on manual dispatch. It writes the current text report to the GitHub Actions step summary.

The scheduled workflow does not mutate `data/projects.json` and does not fail merely because items are due for recheck.
