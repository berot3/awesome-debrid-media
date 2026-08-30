#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build.py"
text = BUILD.read_text(encoding="utf-8")

replacements = [
    (
        '    archived_badge = \'<span class="pill pill--warning">Archived</span>\' if archived else ""\n\n    return f"""\n      <article class="project-card filterable" {data_attrs(project)}>',
        '    archived_badge = \'<span class="pill pill--warning">Archived</span>\' if archived else ""\n    dependency = "Independent" if project["dependency"] == "independent" else "External server / plugin"\n\n    return f"""\n      <article class="project-card filterable" data-project-id="{esc(project[\'id\'])}" {data_attrs(project)}>',
    ),
    (
        '          <div><span>Jellyfin API</span><strong>{esc(CAPABILITY_LABELS[project[\'api\'][\'jellyfin_compatible\']])}</strong></div>\n        </div>\n        <p class="small"><strong>Debrid providers:</strong> {esc(providers)}</p>',
        '          <div><span>Jellyfin API</span><strong>{esc(CAPABILITY_LABELS[project[\'api\'][\'jellyfin_compatible\']])}</strong></div>\n          <div><span>Backend model</span><strong>{esc(dependency)}</strong></div>\n        </div>\n        <p class="small"><strong>Debrid providers:</strong> {esc(providers)}</p>',
    ),
    (
        '        <p class="small"><strong>GitHub:</strong> {esc(stars)} · last push {esc(pushed)} · <strong>verified:</strong> {esc(project[\'verified_at\'])}</p>\n        <details>',
        '        <p class="small"><strong>GitHub:</strong> {esc(stars)} · last push {esc(pushed)} · <strong>verified:</strong> {esc(project[\'verified_at\'])}</p>\n        <button class="select-project" type="button" data-select-project="{esc(project[\'id\'])}" aria-pressed="false">Add to compare</button>\n        <details>',
    ),
    (
        '      <tr id="project-{esc(project[\'id\'])}" class="filterable" {data_attrs(project)}>',
        '      <tr id="project-{esc(project[\'id\'])}" class="filterable" data-project-id="{esc(project[\'id\'])}" {data_attrs(project)}>',
    ),
    (
        '          <a class="table-evidence-link" href="#evidence-{esc(project[\'id\'])}" aria-label="Evidence &amp; notes for {esc(project[\'name\'])}">Evidence &amp; notes</a>\n        </th>',
        '          <a class="table-evidence-link" href="#evidence-{esc(project[\'id\'])}" aria-label="Evidence &amp; notes for {esc(project[\'name\'])}">Evidence &amp; notes</a>\n          <button class="select-project table-select-project" type="button" data-select-project="{esc(project[\'id\'])}" aria-pressed="false">Add to compare</button>\n        </th>',
    ),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit(f"expected Issue 33 target not found: {old[:120]}")

css_marker = '    .empty-state p {{ margin: 0 0 .7rem; }}\n'
css = '''    .shortlist-toolbar {{ display: flex; flex-wrap: wrap; align-items: center; gap: .65rem; margin: 0 0 1.4rem; padding: .75rem .9rem; border: 1px solid var(--border); border-radius: 1rem; background: var(--soft); }}
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
'''
if css not in text:
    if css_marker not in text:
        raise SystemExit("expected shortlist CSS marker not found")
    text = text.replace(css_marker, css_marker + css, 1)

html_marker = '''    <section id="empty-state" class="empty-state hidden" aria-label="No matching projects">
      <p><strong>No projects match the current filters.</strong> Broaden the search or reset the comparison.</p>
      <button id="empty-reset" type="button">Reset filters</button>
    </section>

'''
shortlist_html = '''    <section id="shortlist-toolbar" class="shortlist-toolbar hidden" aria-label="Selected projects">
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

'''
if shortlist_html not in text:
    if html_marker not in text:
        raise SystemExit("expected shortlist HTML marker not found")
    text = text.replace(html_marker, html_marker + shortlist_html, 1)

const_marker = "      const emptyState = document.querySelector('#empty-state');\n      const filters = document.querySelector('.filters');\n"
consts = """      const emptyState = document.querySelector('#empty-state');
      const shortlistToolbar = document.querySelector('#shortlist-toolbar');
      const shortlistStatus = document.querySelector('#shortlist-status');
      const shortlistOpen = document.querySelector('#shortlist-open');
      const shortlistClear = document.querySelector('#shortlist-clear');
      const shortlistFocus = document.querySelector('#shortlist-focus');
      const shortlistHeading = document.querySelector('#shortlist-heading');
      const shortlistBack = document.querySelector('#shortlist-back');
      const shortlistGrid = document.querySelector('#shortlist-grid');
      const filters = document.querySelector('.filters');
"""
if consts not in text:
    if const_marker not in text:
        raise SystemExit("expected shortlist const marker not found")
    text = text.replace(const_marker, consts, 1)

state_marker = "      const desktopSticky = window.matchMedia('(min-width: 1200px)');\n\n"
state = """      const desktopSticky = window.matchMedia('(min-width: 1200px)');
      const shortlistLimit = 4;
      const selectedProjects = new Set();
      const cardSources = new Map([...document.querySelectorAll('.project-card[data-project-id]')].map(card => [card.dataset.projectId, card]));
      let shortlistFocused = false;

"""
if state not in text:
    if state_marker not in text:
        raise SystemExit("expected shortlist state marker not found")
    text = text.replace(state_marker, state, 1)

function_marker = "      function matches(item) {{\n"
functions = """      function syncSelectionButtons() {{
        const atLimit = selectedProjects.size >= shortlistLimit;
        document.querySelectorAll('[data-select-project]').forEach(button => {{
          const selected = selectedProjects.has(button.dataset.selectProject);
          button.setAttribute('aria-pressed', selected ? 'true' : 'false');
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
        if (selectedProjects.has(projectId)) selectedProjects.delete(projectId);
        else if (selectedProjects.size < shortlistLimit) selectedProjects.add(projectId);
        syncShortlistUi();
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
        shortlistOpen.focus();
      }}

      function clearShortlist() {{
        selectedProjects.clear();
        shortlistFocused = false;
        syncShortlistUi();
      }}

"""
if functions not in text:
    if function_marker not in text:
        raise SystemExit("expected shortlist function marker not found")
    text = text.replace(function_marker, functions + function_marker, 1)

events_marker = "      copyShareLink.addEventListener('click', copyCurrentShareLink);\n"
events = """      copyShareLink.addEventListener('click', copyCurrentShareLink);
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
"""
if events not in text:
    if events_marker not in text:
        raise SystemExit("expected shortlist event marker not found")
    text = text.replace(events_marker, events, 1)

init_marker = "      restoreFromUrl();\n      syncStickyTableOffset();\n      apply();\n"
init = """      restoreFromUrl();
      syncStickyTableOffset();
      syncShortlistUi();
      apply();
"""
if init not in text:
    if init_marker not in text:
        raise SystemExit("expected shortlist init marker not found")
    text = text.replace(init_marker, init, 1)

BUILD.write_text(text, encoding="utf-8")
