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
CLIENT_EXPLANATIONS = {
    "released_first_party": "A public first-party Apple TV/tvOS release is available.",
    "source_only_first_party": "First-party tvOS source exists, but no public/installable release is evidenced.",
    "compatible_third_party": "Apple TV playback is available through a compatible third-party client; this is not first-party tvOS support.",
    "unconfirmed": "Current evidence is insufficient to establish an Apple TV path. This does not mean none exists.",
    "none": "Current evidence supports that there is no Apple TV path in scope for this project.",
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
    apple_state = project["clients"]["apple_tv"]["state"]
    return (
        f"<p><strong>AIOStreams:</strong> {esc(project['aiostreams']['note'])}</p>"
        f"<p><strong>Apple TV path:</strong> {esc(CLIENT_LABELS[apple_state])} — {esc(project['clients']['apple_tv']['note'])}</p>"
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


def apple_guide_html() -> str:
    items = []
    for state, label in CLIENT_LABELS.items():
        items.append(
            "<div>"
            f"<dt>{esc(label)}</dt>"
            f"<dd>{esc(CLIENT_EXPLANATIONS[state])}</dd>"
            "</div>"
        )
    return "".join(items)


def architecture_filter_html() -> str:
    items = []
    for state, label in ARCHITECTURE_LABELS.items():
        items.append(
            f'<label class="check filter-option">'
            f'<input type="checkbox" name="architecture" value="{esc(state)}" data-label="{esc(label)}"> '
            f'{esc(label)}</label>'
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
            f'data-architecture="{esc(project["architecture"])}"',
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
    dependency = "Independent" if project["dependency"] == "independent" else "External server / plugin"

    return f"""
      <article class="project-card filterable" data-project-id="{esc(project['id'])}" {data_attrs(project)}>
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
          <div><span>Apple TV path</span><strong>{esc(CLIENT_LABELS[apple_state])}</strong></div>
          <div><span>Jellyfin API</span><strong>{esc(CAPABILITY_LABELS[project['api']['jellyfin_compatible']])}</strong></div>
          <div><span>Backend model</span><strong>{esc(dependency)}</strong></div>
        </div>
        <p class="small"><strong>Debrid providers:</strong> {esc(providers)}</p>
        <p class="small"><strong>GitHub:</strong> {esc(stars)} · last push {esc(pushed)} · <strong>verified:</strong> {esc(project['verified_at'])}</p>
        <button class="select-project" type="button" data-select-project="{esc(project['id'])}" data-project-name="{esc(project['name'])}" aria-label="Add {esc(project['name'])} to comparison" aria-pressed="false">Add to compare</button>
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
      <tr id="project-{esc(project['id'])}" class="filterable" data-project-id="{esc(project['id'])}" {data_attrs(project)}>
        <th scope="row">
          <a href="https://github.com/{esc(project['repository'])}">{esc(project['name'])}</a>
          <small>{esc(project['repository'])}</small>
          <a class="table-evidence-link" href="#evidence-{esc(project['id'])}" aria-label="Evidence &amp; notes for {esc(project['name'])}">Evidence &amp; notes</a>
          <button class="select-project table-select-project" type="button" data-select-project="{esc(project['id'])}" data-project-name="{esc(project['name'])}" aria-label="Add {esc(project['name'])} to comparison" aria-pressed="false">Add to compare</button>
        </th>
        <td>{esc(ARCHITECTURE_LABELS[project['architecture']])}</td>
        <td>{esc(aio)}</td>
        <td>{esc(CAPABILITY_LABELS[project['sources']['debrid']])}{provider_detail}</td>
        <td>{esc(CAPABILITY_LABELS[project['sources']['usenet']])}</td>
        <td>{esc(apple)}</td>
        <td>{esc(CAPABILITY_LABELS[project['api']['jellyfin_compatible']])}</td>
        <td>{esc(dependency)}</td>
        <td>{esc(stars)}{esc(archived_mark)}<small class="metadata-nowrap">push {esc(pushed)}</small></td>
        <td class="metadata-nowrap">{esc(project['verified_at'])}</td>
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
    apple_guide = apple_guide_html()
    architecture_filter = architecture_filter_html()

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
      --sticky-table-top: 0px;
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
    .filters {{ position: sticky; top: 0; z-index: 5; display: grid; grid-template-columns: minmax(0, 1fr); gap: .8rem; margin: 1rem 0 1.4rem; padding: .9rem; border: 1px solid var(--border); border-radius: 1rem; background: color-mix(in srgb, Canvas 94%, transparent); backdrop-filter: blur(16px); }}
    .filter-row {{ display: flex; flex-wrap: wrap; align-items: center; gap: .65rem; }}
    input[type="search"], select, button {{ font: inherit; color: inherit; background: Canvas; border: 1px solid var(--border); border-radius: .7rem; padding: .62rem .75rem; }}
    input[type="search"] {{ flex: 1 1 260px; min-width: 0; }}
    select {{ max-width: 100%; }}
    .filter-menu {{ position: relative; border-top: 0; margin: 0; padding: 0; }}
    .filter-menu > summary {{ list-style: none; cursor: pointer; font: inherit; font-weight: 400; color: inherit; background: Canvas; border: 1px solid var(--border); border-radius: .7rem; padding: .62rem .75rem; white-space: nowrap; }}
    .filter-menu > summary::-webkit-details-marker {{ display: none; }}
    .filter-menu > summary::after {{ content: " ▾"; color: var(--muted); }}
    .filter-menu[open] > summary::after {{ content: " ▴"; }}
    .filter-menu fieldset {{ position: absolute; z-index: 8; top: calc(100% + .35rem); left: 0; display: grid; gap: .25rem; min-width: min(280px, calc(100vw - 2rem)); margin: 0; padding: .65rem .75rem; border: 1px solid var(--border); border-radius: .7rem; background: Canvas; box-shadow: 0 .5rem 1.5rem color-mix(in srgb, CanvasText 12%, transparent); }}
    .filter-menu .filter-option {{ padding: .3rem .1rem; }}
    .filter-menu .preset-option {{ display: grid; gap: .45rem; max-width: min(360px, calc(100vw - 2rem)); }}
    .filter-menu .preset-option p {{ margin: 0; white-space: normal; }}
    .filter-menu .preset-option button {{ text-align: left; white-space: normal; }}
    button {{ cursor: pointer; }}
    button:hover {{ border-color: var(--muted); }}
    .check {{ display: inline-flex; align-items: center; gap: .38rem; padding: .35rem .15rem; white-space: nowrap; }}
    #result-count {{ margin-left: auto; color: var(--muted); font-size: .9rem; }}
    .empty-state {{ margin: 0 0 1.4rem; padding: 1rem 1.1rem; border: 1px dashed var(--border); border-radius: 1rem; background: var(--soft); }}
    .empty-state p {{ margin: 0 0 .7rem; }}
    .shortlist-toolbar {{ display: flex; flex-wrap: wrap; align-items: center; gap: .65rem; margin: 0 0 1.4rem; padding: .75rem .9rem; border: 1px solid var(--border); border-radius: 1rem; background: var(--soft); }}
    #shortlist-status {{ margin-right: auto; color: var(--muted); font-size: .9rem; }}
    .select-project {{ margin-top: .65rem; }}
    .select-project[aria-pressed="true"] {{ border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent); }}
    .table-select-project {{ display: block; margin-top: .35rem; padding: .34rem .5rem; font-size: .78rem; }}
    .shortlist-focus {{ margin: 0 0 1.4rem; padding: 1rem; border: 1px solid var(--border); border-radius: 1rem; background: var(--soft); }}
    .shortlist-focus__header {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: .8rem; margin-bottom: 1rem; }}
    .shortlist-focus__header h2 {{ margin: 0; font-size: 1.35rem; }}
    .shortlist-focus__header p {{ margin: .25rem 0 0; }}
    .shortlist-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 330px), 1fr)); gap: 1rem; }}
    .shortlist-remove {{ margin-bottom: .2rem; }}
    body.shortlist-is-focused .cards, body.shortlist-is-focused .table-wrap, body.shortlist-is-focused .desktop-project-details, body.shortlist-is-focused #empty-state {{ display: none !important; }}
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
    .sr-only {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }}
    .table-wrap {{ display: none; overflow-x: auto; border: 1px solid var(--border); border-radius: 1rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .84rem; }}
    th, td {{ padding: .72rem .65rem; text-align: left; vertical-align: top; border-bottom: 1px solid var(--border); }}
    thead th {{ position: sticky; top: var(--sticky-table-top); z-index: 4; background: Canvas; white-space: nowrap; box-shadow: 0 1px 0 var(--border); }}
    tbody tr:last-child th, tbody tr:last-child td {{ border-bottom: 0; }}
    tbody th {{ min-width: 155px; }}
    tbody th small, td small {{ display: block; margin-top: .18rem; color: var(--muted); font-weight: 400; }}
    .metadata-nowrap {{ white-space: nowrap; }}
    .table-evidence-link {{ display: inline-block; margin-top: .35rem; font-size: .8rem; font-weight: 650; }}
    .desktop-project-details {{ display: none; }}
    .desktop-project-detail {{ scroll-margin-top: 6rem; padding: 1rem 1.1rem; border: 1px solid var(--border); border-radius: 1rem; background: Canvas; }}
    .desktop-project-detail:target {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
    .desktop-project-detail h3 {{ margin: 0; font-size: 1.05rem; }}
    .desktop-project-detail p {{ max-width: 90ch; }}
    .detail-back-link {{ display: inline-block; margin-top: .2rem; font-size: .86rem; font-weight: 650; }}
    .hidden {{ display: none !important; }}
    footer {{ margin-top: 2.5rem; padding-top: 1.2rem; border-top: 1px solid var(--border); color: var(--muted); font-size: .9rem; }}
    @media (max-width: 919px) {{
      .filter-menu[open] {{ flex: 1 0 100%; }}
      .filter-menu fieldset {{ position: static; box-sizing: border-box; width: 100%; min-width: 0; margin-top: .35rem; }}
    }}
    @media (min-width: 920px) {{
      .cards {{ display: none; }}
      .table-wrap {{ display: block; }}
      .desktop-project-details {{ display: grid; gap: .8rem; margin-top: 1.4rem; }}
      .desktop-project-details > h2 {{ margin: 0; font-size: 1.35rem; }}
      .filters {{ grid-template-columns: 1fr; align-items: stretch; }}
      .filter-row:first-child {{ min-width: 0; }}
    }}
    @media (min-width: 1200px) {{
      .table-wrap {{ overflow: visible; }}
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
      <p><strong>Apple TV paths are not equivalent.</strong> A public first-party tvOS release, first-party source code, and a compatible third-party client are different support paths. The comparison keeps those states separate:</p>
      <dl class="status-key">
{apple_guide}
      </dl>
      <p class="small"><strong>Search vs. filters:</strong> Text search checks project name, repository, description, architecture and named Debrid providers. Use the AIOStreams, architecture and Apple TV controls for structured filtering.</p>
    </details>

    <section class="filters" aria-label="Comparison filters">
      <div class="filter-row">
        <input id="search" type="search" placeholder="Search name, repo, description, provider…" aria-label="Search project name, repository, description, architecture or Debrid provider">
        <details id="preset-menu" class="filter-menu" name="comparison-filter-menu">
          <summary>Quick filter</summary>
          <fieldset class="preset-option">
            <legend class="sr-only">Use-case presets</legend>
            <button id="preset-aio-apple" type="button">AIOStreams-compatible + Apple TV path</button>
            <p class="small">Sets AIOStreams to “Any compatible path” and Apple TV to “any usable path”. Other filters stay unchanged and can be refined afterward.</p>
          </fieldset>
        </details>
        <select id="aio-filter" aria-label="AIOStreams support">
          <option value="all">All AIOStreams states</option>
          <option value="compatible">Any compatible path (explicit / protocol / bridge)</option>
          <option value="unconfirmed">AIOStreams unconfirmed</option>
          <option value="no-first-party">No first-party / scope conflict</option>
        </select>
        <details id="architecture-filter" class="filter-menu" name="comparison-filter-menu">
          <summary><span id="architecture-summary">Architecture: all</span></summary>
          <fieldset>
            <legend class="sr-only">Architecture types</legend>
{architecture_filter}
          </fieldset>
        </details>
        <select id="dependency-filter" aria-label="Backend dependency">
          <option value="all">Any dependency</option>
          <option value="independent">Independent backend</option>
          <option value="external">Requires another media server / plugin host</option>
        </select>
      </div>
      <div class="filter-row">
        <select id="apple-filter" aria-label="Apple TV client path">
          <option value="all">Any Apple TV state</option>
          <option value="any-path">Apple TV: any usable path</option>
          <option value="released_first_party">Apple TV: first-party release</option>
          <option value="source_only_first_party">Apple TV: first-party source only</option>
          <option value="compatible_third_party">Apple TV: compatible third-party client</option>
          <option value="unconfirmed">Apple TV: unconfirmed</option>
          <option value="none">Apple TV: none</option>
        </select>
        <label class="check"><input id="usenet-filter" type="checkbox"> Usenet</label>
        <label class="check"><input id="jellyfin-filter" type="checkbox"> Jellyfin-compatible API</label>
        <button id="reset" type="button">Reset</button>
        <button id="copy-share-link" type="button" aria-live="polite">Copy share link</button>
        <span id="result-count" role="status" aria-live="polite" aria-atomic="true">{len(projects)} projects shown</span>
      </div>
    </section>

    <section id="empty-state" class="empty-state hidden" aria-label="No matching projects">
      <p><strong>No projects match the current filters.</strong> Broaden the search or reset the comparison.</p>
      <button id="empty-reset" type="button">Reset filters</button>
    </section>

    <section id="shortlist-toolbar" class="shortlist-toolbar hidden" aria-label="Selected projects" tabindex="-1">
      <span id="shortlist-status" role="status" aria-live="polite" aria-atomic="true">0 projects selected · maximum 4</span>
      <button id="shortlist-open" type="button" disabled>Compare selected</button>
      <button id="shortlist-clear" type="button">Clear</button>
    </section>

    <section id="shortlist-focus" class="shortlist-focus hidden" aria-labelledby="shortlist-heading">
      <div class="shortlist-focus__header">
        <div>
          <h2 id="shortlist-heading" tabindex="-1">Selected project comparison</h2>
          <p class="small">Selection is a comparison aid, not a ranking or recommendation.</p>
        </div>
        <button id="shortlist-back" type="button">Back to all projects</button>
      </div>
      <div id="shortlist-grid" class="shortlist-grid"></div>
    </section>

    <section class="cards" aria-label="Project comparison cards">
{cards}
    </section>

    <div class="table-wrap">
      <table>
        <caption class="sr-only">Comparison of self-hosted Debrid and Usenet media projects by architecture, AIOStreams integration, capabilities, Apple TV client path, backend model, GitHub activity and verification date.</caption>
        <thead>
          <tr>
            <th>Project</th><th>Architecture</th><th>AIOStreams</th><th>Debrid</th><th>Usenet</th><th>Apple TV path</th><th>Jellyfin API</th><th>Backend model</th><th>GitHub</th><th>Verified</th>
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
      const architecture = [...document.querySelectorAll('input[name="architecture"]')];
      const architectureSummary = document.querySelector('#architecture-summary');
      const presetMenu = document.querySelector('#preset-menu');
      const presetAioApple = document.querySelector('#preset-aio-apple');
      const apple = document.querySelector('#apple-filter');
      const usenet = document.querySelector('#usenet-filter');
      const jellyfin = document.querySelector('#jellyfin-filter');
      const reset = document.querySelector('#reset');
      const emptyReset = document.querySelector('#empty-reset');
      const copyShareLink = document.querySelector('#copy-share-link');
      const count = document.querySelector('#result-count');
      const emptyState = document.querySelector('#empty-state');
      const shortlistToolbar = document.querySelector('#shortlist-toolbar');
      const shortlistStatus = document.querySelector('#shortlist-status');
      const shortlistOpen = document.querySelector('#shortlist-open');
      const shortlistClear = document.querySelector('#shortlist-clear');
      const shortlistFocus = document.querySelector('#shortlist-focus');
      const shortlistHeading = document.querySelector('#shortlist-heading');
      const shortlistBack = document.querySelector('#shortlist-back');
      const shortlistGrid = document.querySelector('#shortlist-grid');
      const filters = document.querySelector('.filters');
      const items = [...document.querySelectorAll('.filterable')];
      const compatibleAio = new Set(['explicit', 'stremio_protocol', 'plugin_or_bridge']);
      const usableApplePaths = new Set(['released_first_party', 'source_only_first_party', 'compatible_third_party']);
      const externalDeps = new Set({json.dumps(sorted(EXTERNAL_DEPENDENCIES))});
      const desktopSticky = window.matchMedia('(min-width: 1200px)');
      const shortlistLimit = 4;
      const selectedProjects = new Set();
      const cardSources = new Map([...document.querySelectorAll('.project-card[data-project-id]')].map(card => [card.dataset.projectId, card]));
      let shortlistFocused = false;

      function setSelectFromParam(control, value) {{
        const valid = [...control.options].some(option => option.value === value);
        control.value = valid ? value : 'all';
      }}

      function restoreFromUrl() {{
        const params = new URLSearchParams(window.location.search);
        search.value = params.get('q') || '';
        setSelectFromParam(aio, params.get('aio'));
        setSelectFromParam(dependency, params.get('dep'));
        setSelectFromParam(apple, params.get('apple'));
        const selectedArchitectures = new Set(params.getAll('arch'));
        architecture.forEach(control => control.checked = selectedArchitectures.has(control.value));
        usenet.checked = params.get('usenet') === '1';
        jellyfin.checked = params.get('jellyfin') === '1';
      }}

      function urlFromControls() {{
        const params = new URLSearchParams();
        const query = search.value.trim();
        if (query) params.set('q', query);
        if (aio.value !== 'all') params.set('aio', aio.value);
        architecture.filter(control => control.checked).forEach(control => params.append('arch', control.value));
        if (dependency.value !== 'all') params.set('dep', dependency.value);
        if (apple.value !== 'all') params.set('apple', apple.value);
        if (usenet.checked) params.set('usenet', '1');
        if (jellyfin.checked) params.set('jellyfin', '1');
        const queryString = params.toString();
        return window.location.pathname + (queryString ? '?' + queryString : '') + window.location.hash;
      }}

      function syncUrl() {{
        window.history.replaceState(null, '', urlFromControls());
      }}

      async function copyCurrentShareLink() {{
        syncUrl();
        const value = window.location.href;
        let copied = false;
        try {{
          if (navigator.clipboard && window.isSecureContext) {{
            await navigator.clipboard.writeText(value);
            copied = true;
          }}
        }} catch (error) {{
          copied = false;
        }}
        if (!copied) {{
          const helper = document.createElement('textarea');
          helper.value = value;
          helper.setAttribute('readonly', '');
          helper.style.position = 'fixed';
          helper.style.opacity = '0';
          document.body.appendChild(helper);
          helper.select();
          copied = document.execCommand('copy');
          helper.remove();
        }}
        const original = 'Copy share link';
        copyShareLink.textContent = copied ? 'Copied' : 'Copy failed';
        window.setTimeout(() => copyShareLink.textContent = original, 1600);
      }}

      function syncSelectionButtons() {{
        const atLimit = selectedProjects.size >= shortlistLimit;
        document.querySelectorAll('[data-select-project]').forEach(button => {{
          const selected = selectedProjects.has(button.dataset.selectProject);
          button.setAttribute('aria-pressed', selected ? 'true' : 'false');
          const projectName = button.dataset.projectName || 'project';
          button.setAttribute('aria-label', selected ? `Remove ${{projectName}} from comparison` : `Add ${{projectName}} to comparison`);
          button.textContent = selected ? 'Selected' : 'Add to compare';
          button.disabled = !selected && atLimit;
        }});
      }}

      function renderShortlist() {{
        shortlistGrid.replaceChildren();
        selectedProjects.forEach(projectId => {{
          const source = cardSources.get(projectId);
          if (!source) return;
          const clone = source.cloneNode(true);
          clone.classList.remove('hidden', 'filterable');
          clone.querySelectorAll('[data-select-project]').forEach(button => button.remove());
          const remove = document.createElement('button');
          remove.type = 'button';
          remove.className = 'shortlist-remove';
          remove.dataset.shortlistRemove = projectId;
          const projectName = source.querySelector('h2')?.textContent.trim() || 'project';
          remove.setAttribute('aria-label', `Remove ${{projectName}} from shortlist`);
          remove.textContent = 'Remove from shortlist';
          clone.prepend(remove);
          shortlistGrid.appendChild(clone);
        }});
      }}

      function syncShortlistUi() {{
        const size = selectedProjects.size;
        if (size === 0) shortlistFocused = false;
        shortlistToolbar.classList.toggle('hidden', size === 0);
        shortlistFocus.classList.toggle('hidden', !shortlistFocused);
        document.body.classList.toggle('shortlist-is-focused', shortlistFocused);
        shortlistStatus.textContent = `${{size}} project${{size === 1 ? '' : 's'}} selected · maximum ${{shortlistLimit}}`;
        shortlistOpen.disabled = shortlistFocused || size < 2;
        shortlistOpen.textContent = shortlistFocused ? `Viewing selected (${{size}})` : `Compare selected (${{size}})`;
        syncSelectionButtons();
        if (shortlistFocused) renderShortlist();
      }}

      function toggleProjectSelection(projectId) {{
        const wasFocused = shortlistFocused;
        const wasSelected = selectedProjects.has(projectId);
        if (wasSelected) selectedProjects.delete(projectId);
        else if (selectedProjects.size < shortlistLimit) selectedProjects.add(projectId);
        syncShortlistUi();
        if (wasFocused && wasSelected) {{
          const nextRemove = shortlistGrid.querySelector('[data-shortlist-remove]');
          if (nextRemove) nextRemove.focus();
          else search.focus();
        }}
      }}

      function openShortlist() {{
        if (selectedProjects.size < 2) return;
        shortlistFocused = true;
        syncShortlistUi();
        shortlistHeading.focus();
        shortlistFocus.scrollIntoView({{ block: 'start' }});
      }}

      function closeShortlist() {{
        shortlistFocused = false;
        syncShortlistUi();
        shortlistToolbar.focus();
      }}

      function clearShortlist() {{
        selectedProjects.clear();
        shortlistFocused = false;
        syncShortlistUi();
        search.focus();
      }}

      function matches(item) {{
        const query = search.value.trim().toLowerCase();
        if (query && !item.dataset.search.includes(query)) return false;
        const selectedArchitectures = architecture.filter(control => control.checked);
        if (selectedArchitectures.length && !selectedArchitectures.some(control => control.value === item.dataset.architecture)) return false;
        if (aio.value === 'compatible' && !compatibleAio.has(item.dataset.aio)) return false;
        if (aio.value === 'unconfirmed' && item.dataset.aio !== 'unconfirmed') return false;
        if (aio.value === 'no-first-party' && !['none', 'scope_conflict'].includes(item.dataset.aio)) return false;
        if (dependency.value === 'independent' && item.dataset.dependency !== 'independent') return false;
        if (dependency.value === 'external' && !externalDeps.has(item.dataset.dependency)) return false;
        if (apple.value === 'any-path' && !usableApplePaths.has(item.dataset.apple)) return false;
        if (!['all', 'any-path'].includes(apple.value) && item.dataset.apple !== apple.value) return false;
        if (usenet.checked && item.dataset.usenet !== 'yes') return false;
        if (jellyfin.checked && item.dataset.jellyfin !== 'yes') return false;
        return true;
      }}

      function applyAioApplePreset() {{
        aio.value = 'compatible';
        apple.value = 'any-path';
        presetMenu.open = false;
        apply();
      }}

      function syncArchitectureSummary() {{
        const selected = architecture.filter(control => control.checked);
        if (selected.length === 0) architectureSummary.textContent = 'Architecture: all';
        else if (selected.length === 1) architectureSummary.textContent = `Architecture: ${{selected[0].dataset.label}}`;
        else architectureSummary.textContent = `Architecture: ${{selected.length}} selected`;
      }}

      function syncStickyTableOffset() {{
        const offset = desktopSticky.matches ? Math.ceil(filters.getBoundingClientRect().height + 8) : 0;
        document.documentElement.style.setProperty('--sticky-table-top', `${{offset}}px`);
      }}

      function apply(syncState = true) {{
        syncArchitectureSummary();
        items.forEach(item => item.classList.toggle('hidden', !matches(item)));
        const visibleCards = [...document.querySelectorAll('.project-card.filterable')].filter(item => !item.classList.contains('hidden')).length;
        count.textContent = `${{visibleCards}} project${{visibleCards === 1 ? '' : 's'}} shown`;
        emptyState.classList.toggle('hidden', visibleCards !== 0);
        if (syncState) syncUrl();
      }}

      function resetFilters() {{
        search.value = '';
        aio.value = 'all';
        dependency.value = 'all';
        architecture.forEach(control => control.checked = false);
        apple.value = 'all';
        usenet.checked = false;
        jellyfin.checked = false;
        apply();
      }}

      [search, aio, dependency, apple, usenet, jellyfin, ...architecture].forEach(control => control.addEventListener('input', apply));
      presetAioApple.addEventListener('click', applyAioApplePreset);
      reset.addEventListener('click', resetFilters);
      emptyReset.addEventListener('click', resetFilters);
      copyShareLink.addEventListener('click', copyCurrentShareLink);
      document.addEventListener('click', event => {{
        const selectButton = event.target.closest('[data-select-project]');
        if (selectButton) {{
          toggleProjectSelection(selectButton.dataset.selectProject);
          return;
        }}
        const removeButton = event.target.closest('[data-shortlist-remove]');
        if (removeButton) toggleProjectSelection(removeButton.dataset.shortlistRemove);
      }});
      shortlistOpen.addEventListener('click', openShortlist);
      shortlistBack.addEventListener('click', closeShortlist);
      shortlistClear.addEventListener('click', clearShortlist);
      window.addEventListener('popstate', () => {{
        restoreFromUrl();
        apply(false);
      }});
      window.addEventListener('resize', syncStickyTableOffset);
      if ('ResizeObserver' in window) new ResizeObserver(syncStickyTableOffset).observe(filters);
      restoreFromUrl();
      syncStickyTableOffset();
      syncShortlistUi();
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
