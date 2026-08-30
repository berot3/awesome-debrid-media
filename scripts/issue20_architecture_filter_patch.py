#!/usr/bin/env python3
from pathlib import Path

path = Path('scripts/build.py')
text = path.read_text(encoding='utf-8')


def replace_once(old: str, new: str) -> None:
    global text
    if text.count(old) != 1:
        raise SystemExit(f'expected exactly one match, found {text.count(old)} for:\n{old[:160]}')
    text = text.replace(old, new, 1)


replace_once(
'''            f'data-search="{esc(search_blob(project))}"',
            f'data-aio="{esc(project["aiostreams"]["state"])}"',
''',
'''            f'data-search="{esc(search_blob(project))}"',
            f'data-architecture="{esc(project["architecture"])}"',
            f'data-aio="{esc(project["aiostreams"]["state"])}"',
''')

replace_once(
'''def github_html(metadata: dict) -> tuple[str, str, str]:
''',
'''def architecture_filter_html() -> str:
    items = []
    for state, label in ARCHITECTURE_LABELS.items():
        items.append(
            f'<label class="check filter-option">'
            f'<input type="checkbox" name="architecture" value="{esc(state)}" data-label="{esc(label)}"> '
            f'{esc(label)}</label>'
        )
    return "".join(items)


def github_html(metadata: dict) -> tuple[str, str, str]:
''')

replace_once(
'''    aio_guide = aio_guide_html()
    apple_guide = apple_guide_html()
''',
'''    aio_guide = aio_guide_html()
    apple_guide = apple_guide_html()
    architecture_filter = architecture_filter_html()
''')

replace_once(
'''    select {{ max-width: 100%; }}
    button {{ cursor: pointer; }}
''',
'''    select {{ max-width: 100%; }}
    .filter-menu {{ position: relative; border-top: 0; margin: 0; padding: 0; }}
    .filter-menu > summary {{ list-style: none; cursor: pointer; font: inherit; font-weight: 400; color: inherit; background: Canvas; border: 1px solid var(--border); border-radius: .7rem; padding: .62rem .75rem; white-space: nowrap; }}
    .filter-menu > summary::-webkit-details-marker {{ display: none; }}
    .filter-menu > summary::after {{ content: " ▾"; color: var(--muted); }}
    .filter-menu[open] > summary::after {{ content: " ▴"; }}
    .filter-menu fieldset {{ position: absolute; z-index: 8; top: calc(100% + .35rem); left: 0; display: grid; gap: .25rem; min-width: min(280px, calc(100vw - 2rem)); margin: 0; padding: .65rem .75rem; border: 1px solid var(--border); border-radius: .7rem; background: Canvas; box-shadow: 0 .5rem 1.5rem color-mix(in srgb, CanvasText 12%, transparent); }}
    .filter-menu .filter-option {{ padding: .3rem .1rem; }}
    button {{ cursor: pointer; }}
''')

replace_once(
'''      <p class="small"><strong>Search vs. filters:</strong> Text search checks project name, repository, description, architecture and named Debrid providers. Use the AIOStreams and Apple TV controls for structured compatibility/path filtering.</p>
''',
'''      <p class="small"><strong>Search vs. filters:</strong> Text search checks project name, repository, description, architecture and named Debrid providers. Use the AIOStreams, architecture and Apple TV controls for structured filtering.</p>
''')

replace_once(
'''        <select id="dependency-filter" aria-label="Backend dependency">
          <option value="all">Any dependency</option>
          <option value="independent">Independent backend</option>
          <option value="external">Requires another media server / plugin host</option>
        </select>
''',
'''        <details id="architecture-filter" class="filter-menu">
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
''')

replace_once(
'''      const dependency = document.querySelector('#dependency-filter');
      const apple = document.querySelector('#apple-filter');
''',
'''      const dependency = document.querySelector('#dependency-filter');
      const architecture = [...document.querySelectorAll('input[name="architecture"]')];
      const architectureSummary = document.querySelector('#architecture-summary');
      const apple = document.querySelector('#apple-filter');
''')

replace_once(
'''        if (aio.value === 'compatible' && !compatibleAio.has(item.dataset.aio)) return false;
        if (aio.value === 'unconfirmed' && item.dataset.aio !== 'unconfirmed') return false;
''',
'''        const selectedArchitectures = architecture.filter(control => control.checked);
        if (selectedArchitectures.length && !selectedArchitectures.some(control => control.value === item.dataset.architecture)) return false;
        if (aio.value === 'compatible' && !compatibleAio.has(item.dataset.aio)) return false;
        if (aio.value === 'unconfirmed' && item.dataset.aio !== 'unconfirmed') return false;
''')

replace_once(
'''      function syncStickyTableOffset() {{
''',
'''      function syncArchitectureSummary() {{
        const selected = architecture.filter(control => control.checked);
        if (selected.length === 0) architectureSummary.textContent = 'Architecture: all';
        else if (selected.length === 1) architectureSummary.textContent = `Architecture: ${{selected[0].dataset.label}}`;
        else architectureSummary.textContent = `Architecture: ${{selected.length}} selected`;
      }}

      function syncStickyTableOffset() {{
''')

replace_once(
'''      function apply() {{
        items.forEach(item => item.classList.toggle('hidden', !matches(item)));
''',
'''      function apply() {{
        syncArchitectureSummary();
        items.forEach(item => item.classList.toggle('hidden', !matches(item)));
''')

replace_once(
'''        dependency.value = 'all';
        apple.value = 'all';
''',
'''        dependency.value = 'all';
        architecture.forEach(control => control.checked = false);
        apple.value = 'all';
''')

replace_once(
'''      [search, aio, dependency, apple, usenet, jellyfin].forEach(control => control.addEventListener('input', apply));
''',
'''      [search, aio, dependency, apple, usenet, jellyfin, ...architecture].forEach(control => control.addEventListener('input', apply));
''')

path.write_text(text, encoding='utf-8')
