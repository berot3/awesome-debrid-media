#!/usr/bin/env python3
"""Build the static Awesome Debrid Media site from curated project data."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "projects.json"
DIST_DIR = ROOT / "dist"

AIO_LABELS = {
    "explicit": "Confirmed",
    "stremio_protocol": "Stremio protocol",
    "plugin_or_bridge": "Plugin / bridge",
    "unconfirmed": "Unconfirmed",
    "none": "No first-party support",
    "scope_conflict": "Scope conflict",
}


def project_card(project: dict) -> str:
    name = html.escape(project["name"])
    repo = html.escape(project["repository"])
    description = html.escape(project["description"])
    architecture = html.escape(project["architecture"].replace("_", " "))
    aio_state = project["aiostreams"]["state"]
    aio_label = html.escape(AIO_LABELS[aio_state])
    verified = html.escape(project["verified_at"])
    repo_url = f"https://github.com/{repo}"

    return f"""
      <article class="project-card">
        <div class="project-card__header">
          <h2>{name}</h2>
          <span class="status status--{html.escape(aio_state)}">{aio_label}</span>
        </div>
        <p>{description}</p>
        <dl>
          <div><dt>Architecture</dt><dd>{architecture}</dd></div>
          <div><dt>Repository</dt><dd><a href="{repo_url}">{repo}</a></dd></div>
          <div><dt>Verified</dt><dd>{verified}</dd></div>
        </dl>
      </article>
    """


def main() -> int:
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    projects = data["projects"]
    cards = "\n".join(project_card(project) for project in projects)
    if not cards:
        cards = '<p class="empty-state">The comparison dataset is being researched. Project records will appear here once evidence review is complete.</p>'

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>Awesome Debrid Media</title>
  <meta name="description" content="Evidence-based comparison of self-hosted media servers, streaming backends and bridges for Debrid and Usenet.">
  <style>
    :root {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.5; }}
    body {{ margin: 0; }}
    main {{ width: min(1100px, calc(100% - 2rem)); margin: 0 auto; padding: 3rem 0 5rem; }}
    h1 {{ margin-bottom: .5rem; font-size: clamp(2rem, 7vw, 4rem); line-height: 1; }}
    .lede {{ max-width: 70ch; font-size: 1.1rem; }}
    .meta {{ margin: 2rem 0; padding: 1rem; border: 1px solid color-mix(in srgb, CanvasText 20%, transparent); border-radius: .75rem; }}
    .projects {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 290px), 1fr)); gap: 1rem; }}
    .project-card {{ padding: 1rem; border: 1px solid color-mix(in srgb, CanvasText 20%, transparent); border-radius: .9rem; }}
    .project-card__header {{ display: flex; gap: .75rem; align-items: flex-start; justify-content: space-between; }}
    .project-card h2 {{ margin: 0; }}
    .status {{ padding: .2rem .55rem; border: 1px solid currentColor; border-radius: 999px; font-size: .8rem; white-space: nowrap; }}
    dl {{ margin-bottom: 0; }}
    dl div {{ display: grid; grid-template-columns: 8rem 1fr; gap: .5rem; margin-top: .4rem; }}
    dt {{ font-weight: 600; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    a {{ color: inherit; }}
    .empty-state {{ padding: 2rem; border: 1px dashed color-mix(in srgb, CanvasText 35%, transparent); border-radius: .9rem; }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Awesome Debrid Media</h1>
      <p class="lede">A curated, evidence-based comparison of self-hosted media servers, streaming backends, bridges and media-automation systems for Debrid &amp; Usenet.</p>
    </header>
    <section class="meta" aria-label="About this comparison">
      <strong>{len(projects)} project(s) in the current curated dataset.</strong>
      <p>Inclusion is not endorsement. Compatibility claims are classified by evidence, and volatile GitHub metadata is kept separate from manually curated facts.</p>
    </section>
    <section class="projects" aria-label="Projects">
{cards}
    </section>
  </main>
</body>
</html>
"""

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    output = DIST_DIR / "index.html"
    output.write_text(document, encoding="utf-8")
    print(f"built {output.relative_to(ROOT)} with {len(projects)} project(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
