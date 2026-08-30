#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build.py"
text = BUILD.read_text(encoding="utf-8")

replacements = [
    (
        '        <button id="reset" type="button">Reset</button>\n        <span id="result-count" role="status" aria-live="polite" aria-atomic="true">{len(projects)} projects shown</span>',
        '        <button id="reset" type="button">Reset</button>\n        <button id="copy-share-link" type="button" aria-live="polite">Copy share link</button>\n        <span id="result-count" role="status" aria-live="polite" aria-atomic="true">{len(projects)} projects shown</span>',
    ),
    (
        "      const emptyReset = document.querySelector('#empty-reset');\n      const count = document.querySelector('#result-count');",
        "      const emptyReset = document.querySelector('#empty-reset');\n      const copyShareLink = document.querySelector('#copy-share-link');\n      const count = document.querySelector('#result-count');",
    ),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit(f"expected Issue 32 target not found: {old}")

marker = "      function matches(item) {{{{\n"
helpers = """      function setSelectFromParam(control, value) {{{{
        const valid = [...control.options].some(option => option.value === value);
        control.value = valid ? value : 'all';
      }}}}

      function restoreFromUrl() {{{{
        const params = new URLSearchParams(window.location.search);
        search.value = params.get('q') || '';
        setSelectFromParam(aio, params.get('aio'));
        setSelectFromParam(dependency, params.get('dep'));
        setSelectFromParam(apple, params.get('apple'));
        const selectedArchitectures = new Set(params.getAll('arch'));
        architecture.forEach(control => control.checked = selectedArchitectures.has(control.value));
        usenet.checked = params.get('usenet') === '1';
        jellyfin.checked = params.get('jellyfin') === '1';
      }}}}

      function urlFromControls() {{{{
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
      }}}}

      function syncUrl() {{{{
        window.history.replaceState(null, '', urlFromControls());
      }}}}

      async function copyCurrentShareLink() {{{{
        syncUrl();
        const value = window.location.href;
        let copied = false;
        try {{{{
          if (navigator.clipboard && window.isSecureContext) {{{{
            await navigator.clipboard.writeText(value);
            copied = true;
          }}}}
        }}}} catch (error) {{{{
          copied = false;
        }}}}
        if (!copied) {{{{
          const helper = document.createElement('textarea');
          helper.value = value;
          helper.setAttribute('readonly', '');
          helper.style.position = 'fixed';
          helper.style.opacity = '0';
          document.body.appendChild(helper);
          helper.select();
          copied = document.execCommand('copy');
          helper.remove();
        }}}}
        const original = 'Copy share link';
        copyShareLink.textContent = copied ? 'Copied' : 'Copy failed';
        window.setTimeout(() => copyShareLink.textContent = original, 1600);
      }}}}

"""
if helpers not in text:
    if marker not in text:
        raise SystemExit("expected matches() marker not found")
    text = text.replace(marker, helpers + marker, 1)

old_apply = """      function apply() {{{{
        syncArchitectureSummary();
        items.forEach(item => item.classList.toggle('hidden', !matches(item)));
        const visibleCards = [...document.querySelectorAll('.project-card.filterable')].filter(item => !item.classList.contains('hidden')).length;
        count.textContent = `${{visibleCards}} project${{visibleCards === 1 ? '' : 's'}} shown`;
        emptyState.classList.toggle('hidden', visibleCards !== 0);
      }}}}
"""
new_apply = """      function apply(syncState = true) {{{{
        syncArchitectureSummary();
        items.forEach(item => item.classList.toggle('hidden', !matches(item)));
        const visibleCards = [...document.querySelectorAll('.project-card.filterable')].filter(item => !item.classList.contains('hidden')).length;
        count.textContent = `${{visibleCards}} project${{visibleCards === 1 ? '' : 's'}} shown`;
        emptyState.classList.toggle('hidden', visibleCards !== 0);
        if (syncState) syncUrl();
      }}}}
"""
if old_apply in text:
    text = text.replace(old_apply, new_apply, 1)
elif new_apply not in text:
    raise SystemExit("expected apply() block not found")

old_events = """      [search, aio, dependency, apple, usenet, jellyfin, ...architecture].forEach(control => control.addEventListener('input', apply));
      presetAioApple.addEventListener('click', applyAioApplePreset);
      reset.addEventListener('click', resetFilters);
      emptyReset.addEventListener('click', resetFilters);
      window.addEventListener('resize', syncStickyTableOffset);
      if ('ResizeObserver' in window) new ResizeObserver(syncStickyTableOffset).observe(filters);
      syncStickyTableOffset();
      apply();
"""
new_events = """      [search, aio, dependency, apple, usenet, jellyfin, ...architecture].forEach(control => control.addEventListener('input', apply));
      presetAioApple.addEventListener('click', applyAioApplePreset);
      reset.addEventListener('click', resetFilters);
      emptyReset.addEventListener('click', resetFilters);
      copyShareLink.addEventListener('click', copyCurrentShareLink);
      window.addEventListener('popstate', () => {{{{
        restoreFromUrl();
        apply(false);
      }}}});
      window.addEventListener('resize', syncStickyTableOffset);
      if ('ResizeObserver' in window) new ResizeObserver(syncStickyTableOffset).observe(filters);
      restoreFromUrl();
      syncStickyTableOffset();
      apply();
"""
if old_events in text:
    text = text.replace(old_events, new_events, 1)
elif new_events not in text:
    raise SystemExit("expected event wiring block not found")

BUILD.write_text(text, encoding="utf-8")
