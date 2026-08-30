#!/usr/bin/env python3
"""Build the static Awesome Debrid Media comparison site."""

from __future__ import annotations

import html
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "projects.json"
DIST_DIR = ROOT / "dist"

AIO_LABELS = {
    "explicit": "✅ Explicit",
    "stremio_protocol": "🔵 Stremio protocol",
    "plugin_or_bridge": "🟣 Plugin / bridge",
    "unconfirmed": "🟡 Unconfirmed",
    "none": "⚪ No first-party support",
    "scope_conflict": "⛔ Scope conflict",
}
AIO_EXPLANATIONS = {
    "explicit": "The project directly documents or implements AIOStreams support.",
    "stremio_protocol": "A generic Stremio-addon path is confirmed for AIOStreams; this is not a bespoke AIOStreams integration.",
    "plugin_or_bridge": "AIOStreams works through an external or optional plugin, bridge, or companion layer.",
    "unconfirmed": "The architecture is relevant, but current evidence is insufficient. This does not mean unsupported.",
    "none": "Durable evidence supports that there is no first-party AIOStreams path.",
    "scope_conflict": "The required remote-stream integration conflicts with documented product direction or permanent non-goals.",
}
ARCHITECTURE_LABELS = {
    "full_media_server": "Full media server",
    "streaming_backend": "Streaming backend",
    "jellyfin_compatible_server": "Jellyfin-compatible server",
    "bridge": "Bridge",
    "media_automation_vfs": "Automation / VFS",
    "media_server_plugin": "Media-server plugin",
    "other": "Other",
}
CLIENT_LABELS = {
    "released_first_party": "✅ First-party release",
    "source_only_first_party": "🧪 First-party source only",
    "compatible_third_party": "🔗 Compatible third-party client",
    "unconfirmed": "🟡 Unconfirmed",
    "none": "⚪ None",
}
CAPABILITY_LABELS = {"yes": "✅ Yes", "no": "⚪ No", "unknown": "🟡 Unknown"}
EXTERNAL_DEPENDENCIES = {
    "requires_jellyfin",
    "requires_plex",
    "requires_emby",
    "requires_media_server",
    "plugin_for_jellyfin",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def github_metadata(repository: str) -> dict:
    if os.getenv("FETCH_GITHUB_METADATA") != "1":
        return {}

    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "awesome-debrid-media-build",
            **(
                {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
                if os.getenv("GITHUB_TOKEN")
                else {}
            ),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"warning: GitHub metadata unavailable for {repository}: {exc}")
        return {}


def evidence_html(project: dict) -> str:
    entries = (
        project["aiostreams"]["evidence"]
        + project["clients"]["apple_tv"]["evidence"]
        + project["evidence"]
    )
    if not entries:
        return '<p class="muted">No positive evidence is attached to this intentionally unconfirmed state.</p>'

    seen: set[tuple[str, str]] = set()
    items: list[str] = []
    for entry in entries:
        key = (entry["claim"], entry["url"])
        if key in seen:
            continue
        seen.add(key)
        items.append(
            "<li>"
            f"{esc(entry['claim'])} "
            f"<a href=\"{esc(entry['url'])}\">source</a> "
            f"<span class=\"evidence-type\">{esc(entry['source_type'].replace('_', ' '))}</span>"
            "</li>"
        )
    return f"<ul class=\"evidence-list\">{''.join(items)}</ul>"


def project_details_html(project: dict) -> str:
    return (
        f"<p><strong>AIOStreams:</strong> {esc(project['aiostreams']['note'])}</p>"
        f"<p><strong>Apple TV:</strong> {esc(project['clients']['apple_tv']['note'])}</p>"
        f"{evidence_html(project)}"
    )


def aio_guide_html() -> str:
    items = []
    for state, label in AIO_LABELS.items():
        items.append(
            "<div>"
            f"<dt>{esc(label)}</dt>"
            f"<dd>{esc(AIO_EXPLANATIONS[state])}</dd>"
            "</div>"
        )
    return "".join(items)


def github_html(metadata: dict) -> tuple[str, str, str]:
    stars = metadata.get("stargazers_count")
    pushed_at = metadata.get("pushed_at")
    archived = metadata.get("archived")
    stars_text = f"⭐ {stars:,}" if isinstance(stars, int) else "—"
    pushed_text = pushed_at[:10] if isinstance(pushed_at, str) and len(pushed_at) >= 10 else "—"
    archived_text = "Archived" if archived is True else ""
    return stars_text, pushed_text, archived_text


def search_blob(project: dict) -> str:
    providers = " ".join(project["sources"]["debrid_providers"])
    return " ".join(
        [
            project["name"],
            project["repository"],
            project["description"],
            project["architecture"],
            providers,
        ]
    ).lower()


def data_attrs(project: dict) -> str:
    apple = project["clients"]["apple_tv"]["state"]
    return " ".join(
        [
            f'data-search="{esc(search_blob(project))}"',
            f'data-aio="{esc(project["aiostreams"]["state"])}"',
            f'data-apple="{esc(apple)}"',
            f'data-usenet="{esc(project["sources"]["usenet"])}"',
            f'data-jellyfin="{esc(project["api"]["jellyfin_compatible"])}"',
            f'data-dependency="{esc(project["dependency"])}"',
        ]
    )


def project_card(project: dict, metadata: dict) -> str:
    aio_state = project["aiostreams"]["state"]
    apple_state = project["clients"]["apple_tv"]["state"]
    stars, pushed, archived = github_html(metadata)
    providers = ", ".join(project["sources"]["debrid_providers"]) or "Not specified"
    archived_badge = '<span class="pill pill--warning">Archived</span>' if archived else ""

    return f"""
      <article class="project-card filterable" {data_attrs(project)}>
        <div class="project-card__topline">
          <div>
            <h2><a href="https://github.com/{esc(project['repository'])}">{esc(project['name'])}</a></h2>
            <a class="repo-link" href="https://github.com/{esc(project['repository'])}">{esc(project['repository'])} (GH)</a>
          </div>
          {archived_badge}
        </div>
        <p>{esc(project['description'])}</p>
        <div class="status-grid">
          <div><span>Architecture</span><strong>{esc(ARCHITECTURE_LABELS[project['architecture']])}</strong></div>
          <div><span>AIOStreams</span><strong>{esc(AIO_LABELS[aio_state])}</strong></div>
          <div><span>Debrid</span><strong>{esc(CAPABILITY_LABELS[project['sources']['debrid']])}</strong></div>
          <div><span>Usenet</span><strong>{esc(CAPABILITY_LABELS[project['sources']['usenet']])}</strong></div>
          <div><span>Apple TV</span><strong>{esc(CLIENT_LABELS[apple_state])}</strong></div>
          <div><span>Jellyfin API</span><strong>{esc(CAPABILITY_LABELS[project['api']['jellyfin_compatible']])}</strong></div>
        </div>
        <p class="small"><strong>Debrid providers:</strong> {esc(providers)}</p>
        <p class="small"><strong>GitHub:</strong> {esc(stars)} · last push {esc(pushed)} · <strong>verified:</strong> {esc(project['verified_at'])}</p>
        <details>
          <summary>Evidence &amp; notes</summary>
          {project_details_html(project)}
        </details>
      </article>
    """


def project_row(project: dict, metadata: dict) -> str:
    stars, pushed, archived = github_html(metadata)
    aio = AIO_LABELS[project["aiostreams"]["state"]]
    apple = CLIENT_LABELS[project["clients"]["apple_tv"]["state"]]
    providers = ", ".join(project["sources"]["debrid_providers"])
    provider_detail = f"<small>{esc(providers)}</small>" if providers else ""
    dependency = "Independent" if project["dependency"] == "independent" else "External server / plugin"
    archived_mark = " · archived" if archived else ""
    return f"""
      <tr id="project-{esc(project['id'])}" class="filterable" {data_attrs(project)}>
        <th scope="row">
          <a href="https://github.com/{esc(project['repository'])}">{esc(project['name'])}</a>
          <small>{esc(project['repository'])}</small>
          <a class="table-evidence-link" href="#evidence-{esc(project['id'])}" aria-label="Evidence &amp; notes for {esc(project['name'])}">Evidence &amp; notes</a>
        </th>
        <td>{esc(ARCHITECTURE_LABELS[project['architecture']])}</td>
        <td>{esc(aio)}</td>
        <td>{esc(CAPABILITY_LABELS[project['sources']['debrid']])}{provider_detail}</td>
        <td>{esc(CAPABILITY_LABELS[project['sources']['usenet']])}</td>
        <td>{esc(apple)}</td>
        <td>{esc(CAPABILITY_LABELS[project['api']['jellyfin_compatible']])}</td>
        <td>{esc(dependency)}</td>
        <td>{esc(stars)}{esc(archived_mark)}<small>push {esc(pushed)}</small></td>
        <td>{esc(project['verified_at'])}</td>
      </tr>
    """


def project_detail(project: dict) -> str:
    return f"""
      <article id="evidence-{esc(project['id'])}" class="desktop-project-detail filterable" aria-labelledby="evidence-{esc(project['id'])}-heading" {data_attrs(project)}>
        <h3 id="evidence-{esc(project['id'])}-heading">{esc(project['name'])}</h3>
        {project_details_html(project)}
        <a class="detail-back-link" href="#project-{esc(project['id'])}">Back to {esc(project['name'])} comparison row</a>
      </article>
    """


def main() -> int:
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    projects = data["projects"]
    metadata = {project["id"]: github_metadata(project["repository"]) for project in projects}
    cards = "\n".join(project_card(project, metadata[project["id"]]) for project in projects)
    rows = "\n".join(project_row(project, metadata[project["id"]]) for project in projects)
    desktop_details = "\n".join(project_detail(project) for project in projects)
    aio_guide = aio_guide_html()

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>Awesome Debrid Media</title>
  <meta name="description" content="Evidence-based comparison of self-hosted media servers, streaming backends and bridges for Debrid and Usenet.">
  <style>
    :root {{
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
      --border: color-mix(in srgb, CanvasText 16%, transparent);
      --soft: color-mix(in srgb, CanvasText 6%, Canvas);
      --muted: color-mix(in srgb, CanvasText 66%, transparent);
      --accent: #5577ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: Canvas; color: CanvasText; }}
    a {{ color: inherit; text-underline-offset: .18em; }}
    main {{ width: min(1480px, calc(100% - 2rem)); margin: 0 auto; padding: clamp(2rem, 5vw, 5rem) 0 5rem; }}
    header {{ max-width: 900px; }}
    h1 {{ margin: 0 0 .8rem; font-size: clamp(2.5rem, 8vw, 5.7rem); line-height: .94; letter-spacing: -.055em; }}
    .lede {{ margin: 0; max-width: 72ch; font-size: clamp(1.05rem, 2vw, 1.35rem); color: var(--muted); }}
    .intro-links {{ display: flex; flex-wrap: wrap; gap: .9rem; margin-top: 1.25rem; font-size: .95rem; }}
    .notice {{ margin: 2rem 0 1.2rem; padding: 1rem 1.1rem; border: 1px solid var(--border); background: var(--soft); border-radius: 1rem; }}
    .comparison-guide {{ margin: 0 0 1.2rem; padding: .9rem 1.1rem; border: 1px solid var(--border); border-radius: 1rem; background: Canvas; }}
    .comparison-guide[open] > summary {{ margin-bottom: .7rem; }}
    .comparison-guide p {{ max-width: 95ch; }}
    .status-key {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr)); gap: .65rem; margin: .8rem 0; }}
    .status-key div {{ padding: .65rem .7rem; border-radius: .7rem; background: var(--soft); }}
    .status-key dt {{ font-weight: 700; }}
    .status-key dd {{ margin: .18rem 0 0; color: var(--muted); font-size: .86rem; }}
    .filters {{ position: sticky; top: 0; z-index: 5; display: grid; gap: .8rem; margin: 1rem 0 1.4rem; padding: .9rem; border: 1px solid var(--border); border-radius: 1rem; background: color-mix(in srgb, Canvas 94%, transparent); backdrop-filter: blur(16px); }}
    .filter-row {{ display: flex; flex-wrap: wrap; align-items: center; gap: .65rem; }}
    input[type="search"], select, button {{ font: inherit; color: inherit; background: Canvas; border: 1px solid var(--border); border-radius: .7rem; padding: .62rem .75rem; }}
    input[type="search"] {{ flex: 1 1 260px; min-width: 0; }}
    select {{ max-width: 100%; }}
    button {{ cursor: pointer; }}
    button:hover {{ border-color: var(--muted); }}
    .check {{ display: inline-flex; align-items: center; gap: .38rem; padding: .35rem .15rem; white-space: nowrap; }}
    #result-count {{ margin-left: auto; color: var(--muted); font-size: .9rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 330px), 1fr)); gap: 1rem; }}
    .project-card {{ padding: 1.05rem; border: 1px solid var(--border); border-radius: 1rem; background: Canvas; }}
    .project-card__topline {{ display: flex; justify-content: space-between; gap: .7rem; align-items: flex-start; }}
    .project-card h2 {{ margin: 0; font-size: 1.35rem; }}
    .repo-link {{ display: inline-block; margin-top: .15rem; color: var(--muted); font-size: .85rem; text-decoration: none; overflow-wrap: anywhere; }}
    .pill {{ display: inline-block; border: 1px solid currentColor; border-radius: 999px; padding: .14rem .48rem; font-size: .72rem; }}
    .pill--warning {{ color: #b05a00; }}
    .status-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: .55rem; margin: 1rem 0; }}
    .status-grid div {{ min-width: 0; padding: .55rem; border-radius: .7rem; background: var(--soft); }}
    .status-grid span, .status-grid strong {{ display: block; }}
    .status-grid span {{ color: var(--muted); font-size: .72rem; text-transform: uppercase; letter-spacing: .04em; }}
    .status-grid strong {{ margin-top: .12rem; font-size: .86rem; overflow-wrap: anywhere; }}
    .small {{ font-size: .86rem; color: var(--muted); }}
    details {{ border-top: 1px solid var(--border); margin-top: .9rem; padding-top: .7rem; }}
    summary {{ cursor: pointer; font-weight: 650; }}
    .comparison-guide {{ border-top: 1px solid var(--border); margin-top: 0; padding-top: .9rem; }}
    .evidence-list {{ padding-left: 1.2rem; font-size: .86rem; }}
    .evidence-list li {{ margin: .5rem 0; }}
    .evidence-type {{ color: var(--muted); font-size: .75rem; }}
    .muted {{ color: var(--muted); }}
    .table-wrap {{ display: none; overflow-x: auto; border: 1px solid var(--border); border-radius: 1rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .84rem; }}
    th, td {{ padding: .72rem .65rem; text-align: left; vertical-align: top; border-bottom: 1px solid var(--border); }}
    thead th {{ position: sticky; top: 0; background: Canvas; white-space: nowrap; }}
    tbody tr:last-child th, tbody tr:last-child td {{ border-bottom: 0; }}
    tbody th {{ min-width: 155px; }}
    tbody th small, td small {{ display: block; margin-top: .18rem; color: var(--muted); font-weight: 400; }}
    .table-evidence-link {{ display: inline-block; margin-top: .35rem; font-size: .8rem; font-weight: 650; }}
    .desktop-project-details {{ display: none; }}
    .desktop-project-detail {{ scroll-margin-top: 6rem; padding: 1rem 1.1rem; border: 1px solid var(--border); border-radius: 1rem; background: Canvas; }}
    .desktop-project-detail:target {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
    .desktop-project-detail h3 {{ margin: 0; font-size: 1.05rem; }}
    .desktop-project-detail p {{ max-width: 90ch; }}
    .detail-back-link {{ display: inline-block; margin-top: .2rem; font-size: .86rem; font-weight: 650; }}
    .hidden {{ display: none !important; }}
    footer {{ margin-top: 2.5rem; padding-top: 1.2rem; border-top: 1px solid var(--border); color: var(--muted); font-size: .9rem; }}
    @media (min-width: 920px) {{
      .cards {{ display: none; }}
      .table-wrap {{ display: block; }}
      .desktop-project-details {{ display: grid; gap: .8rem; margin-top: 1.4rem; }}
      .desktop-project-details > h2 {{ margin: 0; font-size: 1.35rem; }}
      .filters {{ grid-template-columns: 1fr auto; align-items: center; }}
      .filter-row:first-child {{ min-width: 0; }}
    }}
    @media (max-width: 560px) {{
      main {{ width: min(100% - 1rem, 1480px); }}
      .filters {{ position: static; }}
      .status-grid {{ grid-template-columns: 1fr; }}
      #result-count {{ width: 100%; margin-left: 0; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Awesome Debrid Media</h1>
      <p class="lede">A curated, evidence-based comparison of self-hosted media servers, streaming backends, bridges and media-automation systems for Debrid &amp; Usenet.</p>
      <nav class="intro-links" aria-label="Project links">
        <a href="https://github.com/berot3/awesome-debrid-media">GitHub repository</a>
        <a href="https://github.com/berot3/awesome-debrid-media/blob/master/docs/methodology.md">Methodology</a>
        <a href="https://github.com/berot3/awesome-debrid-media/blob/master/CONTRIBUTING.md">Contribute / correct data</a>
      </nav>
    </header>

    <section class="notice">
      <strong>{len(projects)} evidence-reviewed projects.</strong>
      Inclusion is not endorsement. “Unconfirmed” means evidence is insufficient, not “unsupported.” GitHub stars are context, never a ranking.
    </section>

    <details class="comparison-guide">
      <summary>How to read this comparison</summary>
      <p><strong>Why AIOStreams?</strong> AIOStreams is a primary comparison dimension because these server-side projects can use it as a stream-source integration point. The path matters: direct support, generic Stremio-protocol compatibility, and plugin/bridge integrations are useful but not equivalent.</p>
      <dl class="status-key">
{aio_guide}
      </dl>
      <p><strong>Why include projects without first-party AIOStreams support?</strong> Inclusion means the architecture is useful to compare in this ecosystem, not that the project is endorsed or AIOStreams-compatible. That is why a project such as Silo can remain visible while being classified accurately.</p>
      <p class="small"><strong>Search vs. filters:</strong> Text search checks project name, repository, description, architecture and named Debrid providers. Use the AIOStreams control for compatibility state. The Apple TV filter groups first-party release, source-only and compatible third-party-client paths.</p>
    </details>

    <section class="filters" aria-label="Comparison filters">
      <div class="filter-row">
        <input id="search" type="search" placeholder="Search name, repo, description, provider…" aria-label="Search project name, repository, description, architecture or Debrid provider">
        <select id="aio-filter" aria-label="AIOStreams support">
          <option value="all">All AIOStreams states</option>
          <option value="compatible">Any compatible path (explicit / protocol / bridge)</option>
          <option value="unconfirmed">AIOStreams unconfirmed</option>
          <option value="no-first-party">No first-party / scope conflict</option>
        </select>
        <select id="dependency-filter" aria-label="Backend dependency">
          <option value="all">Any dependency</option>
          <option value="independent">Independent backend</option>
          <option value="external">Requires another media server / plugin host</option>
        </select>
      </div>
      <div class="filter-row">
        <label class="check"><input id="apple-filter" type="checkbox"> Apple TV: any path</label>
        <label class="check"><input id="usenet-filter" type="checkbox"> Usenet</label>
        <label class="check"><input id="jellyfin-filter" type="checkbox"> Jellyfin-compatible API</label>
        <button id="reset" type="button">Reset</button>
        <span id="result-count">{len(projects)} shown</span>
      </div>
    </section>

    <section class="cards" aria-label="Project comparison cards">
{cards}
    </section>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Project</th><th>Architecture</th><th>AIOStreams</th><th>Debrid</th><th>Usenet</th><th>Apple TV</th><th>Jellyfin API</th><th>Backend model</th><th>GitHub</th><th>Verified</th>
          </tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>

    <section class="desktop-project-details" aria-labelledby="desktop-details-heading">
      <h2 id="desktop-details-heading">Project evidence &amp; notes</h2>
{desktop_details}
    </section>

    <footer>
      Curated facts come from first-party evidence wherever possible. Volatile GitHub metadata is fetched only during the Pages build and is not stored as project truth.
    </footer>
  </main>
  <script>
    (() => {{
      const search = document.querySelector('#search');
      const aio = document.querySelector('#aio-filter');
      const dependency = document.querySelector('#dependency-filter');
      const apple = document.querySelector('#apple-filter');
      const usenet = document.querySelector('#usenet-filter');
      const jellyfin = document.querySelector('#jellyfin-filter');
      const reset = document.querySelector('#reset');
      const count = document.querySelector('#result-count');
      const items = [...document.querySelectorAll('.filterable')];
      const compatibleAio = new Set(['explicit', 'stremio_protocol', 'plugin_or_bridge']);
      const applePaths = new Set(['released_first_party', 'source_only_first_party', 'compatible_third_party']);
      const externalDeps = new Set({json.dumps(sorted(EXTERNAL_DEPENDENCIES))});

      function matches(item) {{
        const query = search.value.trim().toLowerCase();
        if (query && !item.dataset.search.includes(query)) return false;
        if (aio.value === 'compatible' && !compatibleAio.has(item.dataset.aio)) return false;
        if (aio.value === 'unconfirmed' && item.dataset.aio !== 'unconfirmed') return false;
        if (aio.value === 'no-first-party' && !['none', 'scope_conflict'].includes(item.dataset.aio)) return false;
        if (dependency.value === 'independent' && item.dataset.dependency !== 'independent') return false;
        if (dependency.value === 'external' && !externalDeps.has(item.dataset.dependency)) return false;
        if (apple.checked && !applePaths.has(item.dataset.apple)) return false;
        if (usenet.checked && item.dataset.usenet !== 'yes') return false;
        if (jellyfin.checked && item.dataset.jellyfin !== 'yes') return false;
        return true;
      }}

      function apply() {{
        items.forEach(item => item.classList.toggle('hidden', !matches(item)));
        const visibleCards = [...document.querySelectorAll('.project-card.filterable')].filter(item => !item.classList.contains('hidden')).length;
        count.textContent = `${{visibleCards}} shown`;
      }}

      [search, aio, dependency, apple, usenet, jellyfin].forEach(control => control.addEventListener('input', apply));
      reset.addEventListener('click', () => {{
        search.value = '';
        aio.value = 'all';
        dependency.value = 'all';
        apple.checked = false;
        usenet.checked = false;
        jellyfin.checked = false;
        apply();
      }});
      apply();
    }})();
  </script>
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
