#!/usr/bin/env python3
"""Temporary second-pass factual fixups for Issue #3."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "projects.json"
TODAY = "2026-08-30"

with DATA.open("r", encoding="utf-8") as handle:
    doc = json.load(handle)

projects = {project["id"]: project for project in doc["projects"]}

# Mycelium's Full profile has a first-party browser player and explicitly says
# no Jellyfin client is needed, so the backend is not intrinsically dependent
# on a downstream media server even though Jellyfin is its primary target.
projects["mycelium"]["dependency"] = "independent"

# StremThru's current first-party docs expose six built-in Stremio addons,
# including Newz with NNTP streaming. Normalize the provider display name to the
# dataset convention while recording the newly verified Usenet capability.
st = projects["stremthru"]
st["sources"]["debrid_providers"] = [
    "AllDebrid",
    "Debrider",
    "Debrid-Link",
    "EasyDebrid",
    "Offcloud",
    "PikPak",
    "Premiumize",
    "Real-Debrid",
    "TorBox",
    "Torrin",
]
st["sources"]["usenet"] = "yes"
st["description"] = (
    "Stremio-oriented streaming proxy/backend that abstracts multiple Debrid stores, "
    "proxies byte-range media content, and ships built-in Stremio addons for store, "
    "torrent, and Usenet/NNTP streaming."
)
extra = [
    {
        "claim": "First-party documentation says StremThru includes six built-in Stremio addons, including Store, Torz and Newz.",
        "url": "https://github.com/MunifTanjim/stremthru/blob/main/docs/stremio-addons/index.md",
        "source_type": "official_docs",
        "checked_at": TODAY,
    },
    {
        "claim": "The built-in StremThru Newz addon explicitly documents Usenet integration and NNTP streaming.",
        "url": "https://github.com/MunifTanjim/stremthru/blob/main/docs/stremio-addons/newz.md",
        "source_type": "official_docs",
        "checked_at": TODAY,
    },
]
claims = {(entry["claim"], entry["url"]) for entry in st["evidence"]}
for entry in extra:
    if (entry["claim"], entry["url"]) not in claims:
        st["evidence"].append(entry)

with DATA.open("w", encoding="utf-8") as handle:
    json.dump(doc, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
