#!/usr/bin/env python3
"""One-shot, idempotent Issue #4 data-audit patcher.

Temporary helper: apply only evidence-backed updates found during the 2026-08-30
manual re-audit, then remove this file before opening the final PR.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "projects.json"
TODAY = "2026-08-30"

with DATA.open("r", encoding="utf-8") as handle:
    doc = json.load(handle)

projects = {project["id"]: project for project in doc["projects"]}


def touch_url(project: dict, url: str) -> None:
    groups = [project.get("evidence", []), project["aiostreams"].get("evidence", [])]
    clients = project.get("clients", {})
    for client in clients.values():
        if isinstance(client, dict):
            groups.append(client.get("evidence", []))
    for entries in groups:
        for entry in entries:
            if entry.get("url") == url:
                entry["checked_at"] = TODAY


def add_evidence(project: dict, claim: str, url: str, source_type: str) -> None:
    entries = project.setdefault("evidence", [])
    if not any(entry.get("claim") == claim and entry.get("url") == url for entry in entries):
        entries.append(
            {
                "claim": claim,
                "url": url,
                "source_type": source_type,
                "checked_at": TODAY,
            }
        )


# MediaStorm — current README + dedicated scraper rechecked.
p = projects["mediastorm"]
for url in [
    "https://github.com/godver3/mediastorm/blob/master/README.md",
    "https://github.com/godver3/mediastorm/blob/master/backend/services/debrid/scraper_aiostreams.go",
]:
    touch_url(p, url)
p["verified_at"] = TODAY

# Remux — generic Stremio integration remains the AIO classification, but current
# stream handling explicitly consumes AIOStreams NZB/indexer metadata and serves
# returned HTTP URLs, establishing a usable Usenet-via-AIOStreams path.
p = projects["remux"]
p["sources"]["usenet"] = "yes"
p["aiostreams"]["note"] = (
    "Remux implements a generic Stremio-addon preset whose source explicitly says it "
    "includes AIO; current stream handling also consumes AIOStreams-specific streamData "
    "such as NZB/indexer metadata rather than using a separate AIOStreams-only provider."
)
for url in [
    "https://github.com/lostb1t/remux/blob/main/README.md",
    "https://github.com/lostb1t/remux/blob/main/crates/remux-server/src/addons/stremio.rs",
]:
    touch_url(p, url)
add_evidence(
    p,
    "The active Stremio stream path accepts AIOStreams HTTP streams and reads AIOStreams NZB URL/indexer metadata, providing a Usenet-capable remote-stream path through AIOStreams.",
    "https://github.com/lostb1t/remux/blob/main/crates/remux-server/src/addons/stremio.rs",
    "source_code",
)
p["verified_at"] = TODAY

# Fetcherr — README now explicitly documents EasyNews-backed direct URLs returned
# by AIOStreams as playable through the normal resolver.
p = projects["fetcherr"]
p["sources"]["usenet"] = "yes"
touch_url(p, "https://github.com/goneturbo/fetcherr/blob/main/README.md")
add_evidence(
    p,
    "The README explicitly documents AIOStreams configured with EasyNews returning direct playable URLs that Fetcherr can unwrap and play, establishing a Usenet-backed playback path.",
    "https://github.com/goneturbo/fetcherr/blob/main/README.md",
    "readme",
)
p["verified_at"] = TODAY

# Hound — current README still confirms local media, Debrid/Usenet via AIOStreams,
# released Android TV, web frontend, and source-only iOS/tvOS.
p = projects["hound"]
touch_url(p, "https://github.com/Hound-Media-Server/hound/blob/main/README.md")
p["verified_at"] = TODAY

# Riven RS — current generated plugin docs expose concrete StremThru provider
# settings and a direct NNTP-streaming Usenet implementation.
p = projects["riven-rs"]
p["aiostreams"]["note"] = (
    "Riven RS includes a built-in AIOStreams torrent-scraper plugin; its official "
    "plugin docs describe AIOStreams as a scraper that can replace separate Torrentio "
    "and Comet scraper paths."
)
p["sources"]["debrid_providers"] = [
    "Real-Debrid",
    "AllDebrid",
    "Debrider",
    "Debrid-Link",
    "EasyDebrid",
    "Offcloud",
    "PikPak",
    "Premiumize",
    "TorBox",
]
for url in [
    "https://github.com/olivertgwalton/riven-rs/blob/main/README.md",
    "https://github.com/olivertgwalton/riven-rs/blob/main/docs/plugins/aiostreams.md",
]:
    touch_url(p, url)
add_evidence(
    p,
    "The StremThru plugin exposes API-key settings for Real-Debrid, AllDebrid, Debrider, Debrid-Link, EasyDebrid, Offcloud, PikPak, Premiumize, and TorBox.",
    "https://github.com/olivertgwalton/riven-rs/blob/main/docs/plugins/stremthru.md",
    "official_docs",
)
add_evidence(
    p,
    "The built-in Usenet plugin directly streams NZB content from configured NNTP providers through the VFS without staging the full download locally.",
    "https://github.com/olivertgwalton/riven-rs/blob/main/docs/plugins/usenet.md",
    "official_docs",
)
p["verified_at"] = TODAY

# Riven TS — current first-party docs/package inventory still describe
# Torrentio/Comet + StremThru and do not contain an AIOStreams plugin. Preserve
# unconfirmed (not none): absence of a plugin is not an explicit support refusal.
p = projects["riven-ts"]
p["aiostreams"]["note"] = (
    "Current official docs use Torrentio or Comet for scraping and StremThru for "
    "Debrid, and the current package inventory contains those plugins but no "
    "AIOStreams plugin. Because this is absence rather than an explicit unsupported "
    "statement, AIOStreams remains unconfirmed rather than none."
)
p["aiostreams"]["evidence"] = [
    {
        "claim": "Current official Riven TS documentation describes Torrentio or Comet as scraper choices and StremThru as the Debrid layer.",
        "url": "https://github.com/rivenmedia/riven-ts/blob/main/apps/wiki/content/docs/index.mdx",
        "source_type": "official_docs",
        "checked_at": TODAY,
    },
    {
        "claim": "The current packages tree contains dedicated Comet, Torrentio and StremThru plugins but no AIOStreams plugin package; this supports an unconfirmed state, not a negative support claim.",
        "url": "https://github.com/rivenmedia/riven-ts/tree/main/packages",
        "source_type": "source_code",
        "checked_at": TODAY,
    },
]
touch_url(p, "https://github.com/rivenmedia/riven-ts/blob/main/apps/wiki/content/docs/index.mdx")
p["verified_at"] = TODAY

# Silo — the server's permanent non-goals are unchanged, but first-party native
# TV clients are now independently documented and publicly installable.
p = projects["silo"]
for url in [
    "https://github.com/Silo-Server/silo-server/blob/main/README.md",
    "https://github.com/Silo-Server/silo-server/blob/main/docs/non-goals.md",
]:
    touch_url(p, url)
p["clients"]["apple_tv"] = {
    "state": "released_first_party",
    "note": "Silo has an official native tvOS client and distributes current iOS/tvOS beta builds through TestFlight.",
    "evidence": [
        {
            "claim": "The official Silo Apple repository builds a native tvOS client and links a TestFlight beta for the iOS and tvOS apps.",
            "url": "https://github.com/Silo-Server/silo-apple/blob/main/README.md",
            "source_type": "readme",
            "checked_at": TODAY,
        }
    ],
}
p["clients"]["android_tv"] = {
    "state": "released_first_party",
    "note": "Silo has an official Android TV client with installable APKs published on tagged releases.",
    "evidence": [
        {
            "claim": "The official Silo Android repository documents a native Android TV app and links a current Android TV APK from GitHub Releases.",
            "url": "https://github.com/Silo-Server/silo-android/blob/main/README.md",
            "source_type": "readme",
            "checked_at": TODAY,
        }
    ],
}
p["verified_at"] = TODAY

# Jellyio Streams — current README still explicitly requires AIOStreams with at
# least one Debrid/Usenet service and states playback works in every Jellyfin client.
p = projects["jellyio-streams"]
touch_url(p, "https://github.com/wrvines/jellyio-streams/blob/main/README.md")
p["verified_at"] = TODAY

# Gelato — current README still states only AIOStreams is supported and streams
# are resolved/proxied through Jellyfin. Do not infer Usenet support from that alone.
p = projects["gelato"]
touch_url(p, "https://github.com/lostb1t/Gelato/blob/main/README.md")
p["verified_at"] = TODAY

# CineFlow — source proves explicit AIOStreams support, but specifically as an
# infoHash-returning torrent scraper through AIOStreams' search API, not as the
# full AIOStreams remote playback path.
p = projects["cineflow"]
p["aiostreams"]["note"] = (
    "CineFlow has a dedicated AIOStreams scraper, but the integration calls the "
    "AIOStreams search API for infoHash torrent candidates; it is scraper integration "
    "rather than a full AIOStreams remote-playback/Usenet path. The README scraper "
    "summary still does not list AIOStreams."
)
p["aiostreams"]["evidence"] = [
    {
        "claim": "The current AIOStreams scraper authenticates to /api/v1/search, requests infoHash results, and returns those hashes as torrent candidates for CineFlow's normal pipeline.",
        "url": "https://github.com/S0lidByte/CineFlow/blob/main/src/program/services/scrapers/aiostreams.py",
        "source_type": "source_code",
        "checked_at": TODAY,
    }
]
touch_url(p, "https://github.com/S0lidByte/CineFlow/blob/main/README.md")
p["verified_at"] = TODAY

with DATA.open("w", encoding="utf-8") as handle:
    json.dump(doc, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
