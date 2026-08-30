#!/usr/bin/env python3
from pathlib import Path

path = Path('scripts/build.py')
text = path.read_text(encoding='utf-8')


def replace_once(old: str, new: str) -> None:
    global text
    if text.count(old) != 1:
        raise SystemExit(f'expected exactly one match, found {text.count(old)} for: {old[:80]!r}')
    text = text.replace(old, new, 1)

replace_once(
    '    .filter-menu .filter-option {{ padding: .3rem .1rem; }}\n',
    '    .filter-menu .filter-option {{ padding: .3rem .1rem; }}\n'
    '    .filter-menu .preset-option {{ display: grid; gap: .45rem; max-width: min(360px, calc(100vw - 2rem)); }}\n'
    '    .filter-menu .preset-option p {{ margin: 0; white-space: normal; }}\n'
    '    .filter-menu .preset-option button {{ text-align: left; white-space: normal; }}\n'
)

replace_once(
    '      <div class="filter-row">\n        <input id="search" type="search" placeholder="Search name, repo, description, provider…" aria-label="Search project name, repository, description, architecture or Debrid provider">\n',
    '      <div class="filter-row">\n'
    '        <input id="search" type="search" placeholder="Search name, repo, description, provider…" aria-label="Search project name, repository, description, architecture or Debrid provider">\n'
    '        <details id="preset-menu" class="filter-menu">\n'
    '          <summary>Quick filter</summary>\n'
    '          <fieldset class="preset-option">\n'
    '            <legend class="sr-only">Use-case presets</legend>\n'
    '            <button id="preset-aio-apple" type="button">AIOStreams-compatible + Apple TV path</button>\n'
    '            <p class="small">Sets AIOStreams to “Any compatible path” and Apple TV to “any usable path”. Other filters stay unchanged and can be refined afterward.</p>\n'
    '          </fieldset>\n'
    '        </details>\n'
)

replace_once(
    "      const architectureSummary = document.querySelector('#architecture-summary');\n",
    "      const architectureSummary = document.querySelector('#architecture-summary');\n"
    "      const presetMenu = document.querySelector('#preset-menu');\n"
    "      const presetAioApple = document.querySelector('#preset-aio-apple');\n"
)

replace_once(
    '      function syncArchitectureSummary() {{\n',
    "      function applyAioApplePreset() {{\n"
    "        aio.value = 'compatible';\n"
    "        apple.value = 'any-path';\n"
    "        presetMenu.open = false;\n"
    "        apply();\n"
    "      }}\n\n"
    '      function syncArchitectureSummary() {{\n'
)

replace_once(
    "      reset.addEventListener('click', resetFilters);\n",
    "      presetAioApple.addEventListener('click', applyAioApplePreset);\n"
    "      reset.addEventListener('click', resetFilters);\n"
)

path.write_text(text, encoding='utf-8')
