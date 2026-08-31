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

## Structured issue intake

If you are proposing facts rather than editing the repository directly, use the repository's GitHub Issue Forms:

- **Add a project** for a new comparison candidate;
- **Correct project information** for a stale, incorrect, or insufficiently supported existing claim.

The forms deliberately allow `Unknown / not found`. Do not turn missing evidence into a negative capability claim just to complete the form.

Submitted classifications are evidence leads, not trusted project truth. Nothing from an issue form is automatically written into `data/projects.json`.

## Evidence first

Please provide a durable source where possible. Preferred sources are:

1. official documentation;
2. repository source code;
3. official README;
4. official issue, pull request, or release;
5. direct maintainer statement;
6. community source as secondary context.

A missing search result is not evidence that a feature is unsupported.

Preserve the repository's classification rules during both submissions and review:

- generic Debrid support is not proof of AIOStreams support;
- generic Stremio-addon support is not automatically explicit AIOStreams support;
- source-only tvOS is not a public Apple TV release;
- separate Riven implementations must be verified independently and must not inherit facts from one another;
- inclusion is not endorsement.

## Maintainer / agent triage workflow

Treat every submitted issue as a research lead until independently verified.

1. **Scope triage** — confirm the project or correction belongs in the server-side comparison scope. If not, close or redirect it without editing curated data.
2. **Verify first-party evidence** — open the strongest current first-party sources yourself. Do not trust a submitter-provided classification merely because a URL is present.
3. **Classify conservatively** — apply `docs/definitions.md` and `docs/methodology.md`. If evidence is incomplete, preserve `unknown` / `unconfirmed` rather than inferring support or non-support.
4. **Edit curated data only after verification** — make the smallest evidence-backed change in `data/projects.json`. Update `checked_at` / `verified_at` only when the relevant material was actually rechecked.
5. **Validate and build** — run:

   ```bash
   python3 scripts/validate.py
   python3 scripts/build.py
   ```

6. **Review before merge** — inspect the diff for scope, evidence quality, classification semantics, stale-date mistakes, and accidental unrelated changes before merging.

If the submitted evidence is useful but not strong enough for a data change, document the uncertainty in the issue rather than forcing a classification.

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

## Licensing of contributions

The repository uses split permissive licensing by material type. See [`LICENSE`](LICENSE) for the exact scope.

- Contributions to implementation/source code are provided under the **MIT License**.
- Contributions to the curated dataset and repository-authored documentation/content are provided under **CC0 1.0 Universal**.

By submitting a contribution, you agree that your contribution may be distributed under the license that applies to the material you are contributing. No separate contributor license agreement or sign-off process is required.

Only submit material that you have the right to contribute under the applicable license. Referencing third-party project names, evidence links, or factual claims does not relicense third-party trademarks, text, images, screenshots, or other protected material.
