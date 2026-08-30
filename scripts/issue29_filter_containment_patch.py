#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build.py"
text = BUILD.read_text(encoding="utf-8")

replacements = [
    (
        "    .filters {{ position: sticky; top: 0; z-index: 5; display: grid; gap: .8rem;",
        "    .filters {{ position: sticky; top: 0; z-index: 5; display: grid; grid-template-columns: minmax(0, 1fr); gap: .8rem;",
    ),
    (
        '<details id="preset-menu" class="filter-menu">',
        '<details id="preset-menu" class="filter-menu" name="comparison-filter-menu">',
    ),
    (
        '<details id="architecture-filter" class="filter-menu">',
        '<details id="architecture-filter" class="filter-menu" name="comparison-filter-menu">',
    ),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit(f"expected Issue 29 target not found: {old}")

media = """    @media (max-width: 919px) {{{{
      .filter-menu[open] {{{{ flex: 1 0 100%; }}}}
      .filter-menu fieldset {{{{ position: static; box-sizing: border-box; width: 100%; min-width: 0; margin-top: .35rem; }}}}
    }}}}
"""
marker = "    @media (min-width: 920px) {{{{"
if media not in text:
    if marker not in text:
        raise SystemExit("expected 920px media marker not found")
    text = text.replace(marker, media + marker, 1)

BUILD.write_text(text, encoding="utf-8")
