#!/usr/bin/env python3
from pathlib import Path

path = Path('scripts/build.py')
text = path.read_text(encoding='utf-8')

replacements = [
    (
        "            f'data-dependency=\"{esc(project[\"dependency\"])}\"',\n",
        "            f'data-dependency=\"{esc(project[\"dependency\"])}\"',\n"
        "            f'data-project-name=\"{esc(project[\"name\"])}\"',\n"
        "            f'data-architecture-label=\"{esc(ARCHITECTURE_LABELS[project[\"architecture\"]])}\"',\n"
        "            f'data-verified=\"{esc(project[\"verified_at\"])}\"',\n",
    ),
    (
        "      <article id=\"evidence-{esc(project['id'])}\" class=\"desktop-project-detail filterable\" aria-labelledby=\"evidence-{esc(project['id'])}-heading\" {data_attrs(project)}>",
        "      <article id=\"evidence-{esc(project['id'])}\" class=\"desktop-project-detail filterable\" data-project-id=\"{esc(project['id'])}\" aria-labelledby=\"evidence-{esc(project['id'])}-heading\" {data_attrs(project)}>",
    ),
    (
        "        <label class=\"check\"><input id=\"jellyfin-filter\" type=\"checkbox\"> Jellyfin-compatible API</label>\n        <button id=\"reset\" type=\"button\">Reset</button>",
        "        <label class=\"check\"><input id=\"jellyfin-filter\" type=\"checkbox\"> Jellyfin-compatible API</label>\n"
        "        <select id=\"sort-filter\" aria-label=\"Sort projects\">\n"
        "          <option value=\"default\">Sort: curated order</option>\n"
        "          <option value=\"name-asc\">Sort: name A–Z</option>\n"
        "          <option value=\"name-desc\">Sort: name Z–A</option>\n"
        "          <option value=\"architecture\">Sort: architecture</option>\n"
        "          <option value=\"verified-newest\">Sort: verified newest</option>\n"
        "          <option value=\"verified-oldest\">Sort: verified oldest</option>\n"
        "        </select>\n"
        "        <button id=\"reset\" type=\"button\">Reset</button>",
    ),
    (
        "      const jellyfin = document.querySelector('#jellyfin-filter');\n      const reset = document.querySelector('#reset');",
        "      const jellyfin = document.querySelector('#jellyfin-filter');\n"
        "      const sort = document.querySelector('#sort-filter');\n"
        "      const reset = document.querySelector('#reset');",
    ),
    (
        "      const shortlistLimit = 4;\n      const selectedProjects = new Set();\n      const cardSources = new Map([...document.querySelectorAll('.project-card[data-project-id]')].map(card => [card.dataset.projectId, card]));\n      let shortlistFocused = false;",
        "      const shortlistLimit = 4;\n"
        "      const selectedProjects = new Set();\n"
        "      const cardItems = [...document.querySelectorAll('.cards > .project-card[data-project-id]')];\n"
        "      const rowItems = [...document.querySelectorAll('.table-wrap tbody > tr[data-project-id]')];\n"
        "      const detailItems = [...document.querySelectorAll('.desktop-project-details > .desktop-project-detail[data-project-id]')];\n"
        "      const cardSources = new Map(cardItems.map(card => [card.dataset.projectId, card]));\n"
        "      const originalOrder = new Map(cardItems.map((card, index) => [card.dataset.projectId, index]));\n"
        "      const sortCollator = new Intl.Collator(undefined, { sensitivity: 'base', numeric: true });\n"
        "      let shortlistFocused = false;",
    ),
    (
        "      function setSelectFromParam(control, value) {{\n        const valid = [...control.options].some(option => option.value === value);\n        control.value = valid ? value : 'all';\n      }}",
        "      function setSelectFromParam(control, value, fallback = 'all') {{\n"
        "        const valid = [...control.options].some(option => option.value === value);\n"
        "        control.value = valid ? value : fallback;\n"
        "      }}",
    ),
    (
        "        setSelectFromParam(apple, params.get('apple'));\n        const selectedArchitectures",
        "        setSelectFromParam(apple, params.get('apple'));\n"
        "        setSelectFromParam(sort, params.get('sort'), 'default');\n"
        "        const selectedArchitectures",
    ),
    (
        "        if (jellyfin.checked) params.set('jellyfin', '1');\n        const queryString",
        "        if (jellyfin.checked) params.set('jellyfin', '1');\n"
        "        if (sort.value !== 'default') params.set('sort', sort.value);\n"
        "        const queryString",
    ),
    (
        "      function syncSelectionButtons() {{",
        "      function compareProjectElements(a, b) {{\n"
        "        if (!a || !b) return 0;\n"
        "        const originalCompare = (originalOrder.get(a.dataset.projectId) ?? Number.MAX_SAFE_INTEGER) - (originalOrder.get(b.dataset.projectId) ?? Number.MAX_SAFE_INTEGER);\n"
        "        const nameCompare = sortCollator.compare(a.dataset.projectName || '', b.dataset.projectName || '');\n"
        "        let primary = 0;\n"
        "        if (sort.value === 'name-asc') primary = nameCompare;\n"
        "        else if (sort.value === 'name-desc') primary = -nameCompare;\n"
        "        else if (sort.value === 'architecture') primary = sortCollator.compare(a.dataset.architectureLabel || '', b.dataset.architectureLabel || '');\n"
        "        else if (sort.value === 'verified-newest') primary = (b.dataset.verified || '').localeCompare(a.dataset.verified || '');\n"
        "        else if (sort.value === 'verified-oldest') primary = (a.dataset.verified || '').localeCompare(b.dataset.verified || '');\n"
        "        else return originalCompare;\n"
        "        return primary || nameCompare || originalCompare;\n"
        "      }}\n\n"
        "      function applySort() {{\n"
        "        [cardItems, rowItems, detailItems].forEach(group => {{\n"
        "          if (!group.length) return;\n"
        "          const parent = group[0].parentElement;\n"
        "          [...group].sort(compareProjectElements).forEach(item => parent.appendChild(item));\n"
        "        }});\n"
        "        if (shortlistFocused) renderShortlist();\n"
        "      }}\n\n"
        "      function syncSelectionButtons() {{",
    ),
    (
        "        selectedProjects.forEach(projectId => {{",
        "        [...selectedProjects].sort((a, b) => compareProjectElements(cardSources.get(a), cardSources.get(b))).forEach(projectId => {{",
    ),
    (
        "        items.forEach(item => item.classList.toggle('hidden', !matches(item)));\n        const visibleCards",
        "        items.forEach(item => item.classList.toggle('hidden', !matches(item)));\n"
        "        applySort();\n"
        "        const visibleCards",
    ),
    (
        "        jellyfin.checked = false;\n        apply();",
        "        jellyfin.checked = false;\n"
        "        sort.value = 'default';\n"
        "        apply();",
    ),
    (
        "      [search, aio, dependency, apple, usenet, jellyfin, ...architecture].forEach(control => control.addEventListener('input', apply));",
        "      [search, aio, dependency, apple, usenet, jellyfin, sort, ...architecture].forEach(control => control.addEventListener('input', apply));",
    ),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f'marker not found: {old[:100]!r}')
    text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
