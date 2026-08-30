#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build.py"
text = BUILD.read_text(encoding="utf-8")

replacements = [
    (
        '<button class="select-project" type="button" data-select-project="{esc(project[\'id\'])}" aria-pressed="false">Add to compare</button>',
        '<button class="select-project" type="button" data-select-project="{esc(project[\'id\'])}" data-project-name="{esc(project[\'name\'])}" aria-label="Add {esc(project[\'name\'])} to comparison" aria-pressed="false">Add to compare</button>',
    ),
    (
        '<button class="select-project table-select-project" type="button" data-select-project="{esc(project[\'id\'])}" aria-pressed="false">Add to compare</button>',
        '<button class="select-project table-select-project" type="button" data-select-project="{esc(project[\'id\'])}" data-project-name="{esc(project[\'name\'])}" aria-label="Add {esc(project[\'name\'])} to comparison" aria-pressed="false">Add to compare</button>',
    ),
    (
        '<section id="shortlist-toolbar" class="shortlist-toolbar hidden" aria-label="Selected projects">',
        '<section id="shortlist-toolbar" class="shortlist-toolbar hidden" aria-label="Selected projects" tabindex="-1">',
    ),
    (
        "          button.setAttribute('aria-pressed', selected ? 'true' : 'false');\n          button.textContent = selected ? 'Selected' : 'Add to compare';",
        "          button.setAttribute('aria-pressed', selected ? 'true' : 'false');\n          const projectName = button.dataset.projectName || 'project';\n          button.setAttribute('aria-label', selected ? `Remove ${{projectName}} from comparison` : `Add ${{projectName}} to comparison`);\n          button.textContent = selected ? 'Selected' : 'Add to compare';",
    ),
    (
        "          remove.dataset.shortlistRemove = projectId;\n          remove.textContent = 'Remove from shortlist';",
        "          remove.dataset.shortlistRemove = projectId;\n          const projectName = source.querySelector('h2')?.textContent.trim() || 'project';\n          remove.setAttribute('aria-label', `Remove ${{projectName}} from shortlist`);\n          remove.textContent = 'Remove from shortlist';",
    ),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit(f"expected accessibility target not found: {old[:120]}")

old_toggle = """      function toggleProjectSelection(projectId) {{
        if (selectedProjects.has(projectId)) selectedProjects.delete(projectId);
        else if (selectedProjects.size < shortlistLimit) selectedProjects.add(projectId);
        syncShortlistUi();
      }}
"""
new_toggle = """      function toggleProjectSelection(projectId) {{
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
"""
if old_toggle in text:
    text = text.replace(old_toggle, new_toggle, 1)
elif new_toggle not in text:
    raise SystemExit("expected toggleProjectSelection block not found")

old_close = """      function closeShortlist() {{
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
new_close = """      function closeShortlist() {{
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
"""
if old_close in text:
    text = text.replace(old_close, new_close, 1)
elif new_close not in text:
    raise SystemExit("expected close/clear shortlist block not found")

BUILD.write_text(text, encoding="utf-8")
