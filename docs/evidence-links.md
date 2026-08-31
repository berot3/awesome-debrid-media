# Evidence link health

Awesome Debrid Media treats evidence-link health as a **citation-maintenance signal**, not as a factual verdict about a project.

A broken, redirected, rate-limited, or temporarily unreachable evidence URL never proves that the cited capability is false or unsupported.

## Local check

Run:

```bash
python3 scripts/check_evidence_links.py
```

Optional machine-readable output:

```bash
python3 scripts/check_evidence_links.py --format json
```

Useful tuning options for investigation:

```bash
python3 scripts/check_evidence_links.py --timeout 8 --retries 1 --workers 6
```

The checker reads only evidence-entry URLs from `data/projects.json`. Duplicate URLs are checked once and reported with every project/claim that references them.

## Result categories

The checker uses conservative network categories:

- **healthy** — final response is HTTP 2xx and the URL did not move;
- **redirect** — the request reaches a different final URL or returns a redirect response; this is treated as operationally reachable but may need citation cleanup;
- **missing** — confirmed HTTP 404 or 410;
- **ambiguous** — access/auth/rate-limit responses such as 401, 403, 429, or another non-missing 4xx response;
- **transient** — timeout, connection/network failure, or server-side 5xx response.

Only `healthy` and `redirect` are considered normal/reachable outcomes. All other categories are advisory findings that need human/agent inspection.

A `missing`, `ambiguous`, or `transient` result does **not** authorize any capability or classification change.

## Network behavior

The checker is deliberately bounded:

- clear project-specific user-agent;
- HEAD first to avoid downloading evidence pages unnecessarily;
- GET with a one-byte range only when a server rejects HEAD with 405/501;
- configurable per-request timeout;
- limited retries only for transient/network failures;
- bounded concurrency;
- anonymous GitHub responses such as 403/429 remain `ambiguous`, not `missing`.

External-link findings return exit code 0 so they do not break normal validation merely because a third-party site is unavailable. Invalid dataset/configuration or script failures may return non-zero.

## Agent / maintainer remediation

When the report identifies a link that needs attention:

1. **Inspect the source manually.** Confirm whether the URL is genuinely gone, moved, gated, rate-limited, or only temporarily unavailable.
2. **Find the canonical replacement URL when possible.** Prefer the same first-party source or an equally strong current first-party source.
3. **Re-verify the underlying claim.** Do not merely swap URLs without checking that the replacement still supports the stored claim.
4. **Update the evidence URL and `checked_at` only after that actual recheck.** A redirect alone is not permission to refresh dates mechanically.
5. **Preserve uncertainty if verification is no longer possible.** A dead citation by itself does not justify changing AIOStreams, Debrid, Usenet, Apple TV, architecture, or other capability states.
6. Run:

   ```bash
   python3 scripts/validate.py
   python3 scripts/build.py
   python3 scripts/check_evidence_links.py
   ```

7. Review the final diff for accidental classification/date changes before merge.

## Relationship to freshness

Evidence freshness and evidence-link health answer different questions:

- `scripts/freshness.py` asks **when was this claim/source last meaningfully checked?**
- `scripts/check_evidence_links.py` asks **does the stored citation URL currently respond, redirect, or fail?**

Neither maintenance signal independently proves that a project fact changed.

## Scheduled report

The repository runs the evidence-link checker on a weekly schedule and on manual dispatch. The workflow writes the text report into the GitHub Actions step summary.

The scheduled job is read-only and never modifies `data/projects.json`, evidence entries, classifications, `checked_at`, or `verified_at`.
