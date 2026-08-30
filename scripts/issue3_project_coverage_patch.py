#!/usr/bin/env python3
"""One-shot, idempotent data patch for Issue #3.

Temporary branch helper. It appends only the projects accepted by the documented
2026-08-30 ecosystem survey and is removed before the final PR.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "projects.json"
TODAY = "2026-08-30"


def ev(claim: str, url: str, source_type: str = "readme") -> dict:
    return {
        "claim": claim,
        "url": url,
        "source_type": source_type,
        "checked_at": TODAY,
    }


def client(state: str = "unconfirmed", note: str = "No platform-specific playback path was verified for this record.", evidence: list | None = None) -> dict:
    return {"state": state, "note": note, "evidence": evidence or []}


projects_to_add = [
    {
        "id": "jellygrail",
        "name": "JellyGrail",
        "repository": "philamp/jellygrail",
        "description": "Experimental enhanced Jellyfin distribution that merges local, cloud, and Debrid sources through a unified virtual filesystem and synchronizes them to Jellyfin, Kodi, or Plex.",
        "architecture": "full_media_server",
        "dependency": "independent",
        "aiostreams": {
            "state": "unconfirmed",
            "note": "No current first-party AIOStreams integration was confirmed during this survey.",
            "evidence": [],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["Real-Debrid", "Premiumize", "TorBox"],
            "usenet": "unknown",
            "local_media": "yes",
        },
        "api": {"jellyfin_compatible": "yes"},
        "clients": {
            "apple_tv": client(note="JellyGrail exposes Jellyfin/WebDAV/Kodi/Plex paths, but an Apple TV-specific path was not separately verified for this record."),
            "android_tv": client(note="JellyGrail exposes Jellyfin/WebDAV/Kodi/Plex paths, but an Android TV-specific path was not separately verified for this record."),
            "web": client(
                "compatible_third_party",
                "JellyGrail includes Jellyfin with zero-click setup, so browser playback is provided through the bundled upstream Jellyfin web client rather than a separate JellyGrail web player.",
                [ev("The official README says Jellyfin is included with zero-click setup and is one of the supported player paths.", "https://github.com/philamp/jellygrail/blob/main/README.md")],
            ),
        },
        "evidence": [
            ev("The README describes JellyGrail as an enhanced Jellyfin image bridging local, cloud and Debrid sources through JGFS, with Jellyfin included and external Kodi/Plex paths.", "https://github.com/philamp/jellygrail/blob/main/README.md"),
            ev("The README lists native Debrid support for Real-Debrid, Premiumize and TorBox and documents local mount sources.", "https://github.com/philamp/jellygrail/blob/main/README.md"),
        ],
        "verified_at": TODAY,
    },
    {
        "id": "robofuse",
        "name": "RoboFuse",
        "repository": "itsrenoria/robofuse",
        "description": "Real-Debrid bridge that generates and repairs STRM-based libraries for media-server/client stacks such as Jellyfin, Emby, and Infuse.",
        "architecture": "bridge",
        "dependency": "independent",
        "aiostreams": {
            "state": "unconfirmed",
            "note": "No current first-party AIOStreams integration was confirmed during this survey.",
            "evidence": [],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["Real-Debrid"],
            "usenet": "unknown",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="The README names Infuse as a target, but a tvOS-specific compatibility statement was not separately verified for this record."),
            "android_tv": client(note="No Android TV-specific playback path was verified for this record."),
            "web": client(note="RoboFuse provides library-generation/repair services rather than a verified browser playback client."),
        },
        "evidence": [
            ev("The official README describes RoboFuse as a Real-Debrid STRM generator with library repair for Infuse, Jellyfin, and Emby.", "https://github.com/itsrenoria/robofuse/blob/main/README.md")
        ],
        "verified_at": TODAY,
    },
    {
        "id": "jfresolve",
        "name": "Jfresolve",
        "repository": "vicking20/jfresolve",
        "description": "Jellyfin plugin for on-demand external Stremio-addon streams; the maintainer currently marks the Jellyfin 10.11+ line as not actively maintained.",
        "architecture": "media_server_plugin",
        "dependency": "plugin_for_jellyfin",
        "aiostreams": {
            "state": "explicit",
            "note": "The official installation instructions explicitly list AIOStreams among tested Stremio addons.",
            "evidence": [
                ev("The README's installation instructions say the plugin was tested with Torrentio, TorrentioRD, AIOStreams, and MediaFusion.", "https://github.com/vicking20/jfresolve/blob/main/README.md")
            ],
        },
        "stremio_protocol": "yes",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["Real-Debrid"],
            "usenet": "unknown",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="Playback is delegated to Jellyfin clients; Apple TV coverage was not separately verified for this record."),
            "android_tv": client(note="Playback is delegated to Jellyfin clients; Android TV coverage was not separately verified for this record."),
            "web": client(
                "compatible_third_party",
                "Discovery and playback are integrated into the Jellyfin UI rather than provided through a standalone Jfresolve web client.",
                [ev("The README says external search results are discovered directly through the Jellyfin UI and the plugin streams external sources through Jellyfin.", "https://github.com/vicking20/jfresolve/blob/main/README.md")],
            ),
        },
        "evidence": [
            ev("The README describes a Jellyfin plugin that consumes Stremio addon manifests from a Debrid provider and streams external media on demand.", "https://github.com/vicking20/jfresolve/blob/main/README.md"),
            ev("The current version section labels the Jellyfin 10.11+ line 'Not Actively Maintained'.", "https://github.com/vicking20/jfresolve/blob/main/README.md"),
        ],
        "verified_at": TODAY,
    },
    {
        "id": "mycelium",
        "name": "Mycelium",
        "repository": "corveck79/mycelium",
        "description": "On-demand Debrid streaming backend that turns requests into Jellyfin/Emby/Kodi/Plex/Infuse-ready STRM entries and proxies TorBox or Real-Debrid streams with no full local media storage.",
        "architecture": "streaming_backend",
        "dependency": "requires_media_server",
        "aiostreams": {
            "state": "unconfirmed",
            "note": "No current first-party AIOStreams integration was confirmed during this survey.",
            "evidence": [],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["TorBox", "Real-Debrid"],
            "usenet": "unknown",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="The README documents Infuse via WebDAV, but an Apple TV/tvOS-specific statement was not separately verified for this record."),
            "android_tv": client(note="No Android TV-specific playback path was verified for this record."),
            "web": client(
                "released_first_party",
                "The full Mycelium profile includes its own browser web player in addition to the media-server paths.",
                [ev("The official README documents Mycelium's own Discover SPA and browser web-player path.", "https://github.com/corveck79/mycelium/blob/main/README.md")],
            ),
        },
        "evidence": [
            ev("The README describes TorBox and Real-Debrid request-to-stream pipelines, STRM generation/proxying, and Jellyfin/Emby/Kodi/Plex/Infuse outputs.", "https://github.com/corveck79/mycelium/blob/main/README.md")
        ],
        "verified_at": TODAY,
    },
    {
        "id": "seanime",
        "name": "Seanime",
        "repository": "5rahim/seanime",
        "homepage": "https://seanime.app/",
        "description": "Independent anime-focused media server with local-library management, a first-party web interface, and direct torrent/Debrid streaming.",
        "architecture": "full_media_server",
        "dependency": "independent",
        "aiostreams": {
            "state": "unconfirmed",
            "note": "No current first-party AIOStreams integration was confirmed during this survey.",
            "evidence": [],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["TorBox", "Real-Debrid", "AllDebrid", "Premiumize"],
            "usenet": "unknown",
            "local_media": "yes",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="Seanime documents iOS companion/mobile-server apps, but no first-party tvOS client was verified."),
            "android_tv": client(note="Seanime documents Android companion/mobile-server apps, but no Android TV-specific client was verified."),
            "web": client(
                "released_first_party",
                "Seanime ships a first-party web interface with browser direct-play/transcoding support.",
                [ev("The README calls Seanime a media server with a web interface and documents browser direct play/transcoding.", "https://github.com/5rahim/seanime/blob/main/README.md")],
            ),
        },
        "evidence": [
            ev("The official README describes Seanime as a media server with local-library management and torrent/Debrid streaming through TorBox, Real-Debrid, AllDebrid and Premiumize.", "https://github.com/5rahim/seanime/blob/main/README.md")
        ],
        "verified_at": TODAY,
    },
    {
        "id": "debrid-movie-mapper",
        "name": "DebridMovieMapper",
        "repository": "phrontizo/DebridMovieMapper",
        "description": "Rust streaming backend that maps Real-Debrid or TorBox torrent libraries into a TMDB-organized WebDAV filesystem and resolves media bytes lazily from provider CDNs.",
        "architecture": "streaming_backend",
        "dependency": "independent",
        "aiostreams": {
            "state": "unconfirmed",
            "note": "No current first-party AIOStreams integration was confirmed during this survey.",
            "evidence": [],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["Real-Debrid", "TorBox"],
            "usenet": "unknown",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(
                "compatible_third_party",
                "The first-party README explicitly lists Infuse on iOS/tvOS/macOS as a supported WebDAV consumer.",
                [ev("The DebridMovieMapper README explicitly lists Infuse (iOS/tvOS/macOS) among supported consumers.", "https://github.com/phrontizo/DebridMovieMapper/blob/main/README.md")],
            ),
            "android_tv": client(note="No Android TV-specific playback path was verified for this record."),
            "web": client(note="The project exposes WebDAV rather than a verified browser playback client."),
        },
        "evidence": [
            ev("The README describes Real-Debrid/TorBox WebDAV presentation, TMDB organization, lazy CDN reads, and Jellyfin/Plex/Kodi/Infuse usage.", "https://github.com/phrontizo/DebridMovieMapper/blob/main/README.md")
        ],
        "verified_at": TODAY,
    },
    {
        "id": "vibe-debrid",
        "name": "vibeDebrid",
        "repository": "vibeMonarch/vibeDebrid",
        "description": "Real-Debrid media automation system that scrapes and caches releases, waits for a Zurg/rclone mount, and builds symlink libraries for Plex and Jellyfin.",
        "architecture": "media_automation_vfs",
        "dependency": "requires_media_server",
        "aiostreams": {
            "state": "unconfirmed",
            "note": "No current first-party AIOStreams integration was confirmed during this survey.",
            "evidence": [],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["Real-Debrid"],
            "usenet": "unknown",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="Playback is delegated to the downstream media-server/client stack; no Apple TV path was separately verified."),
            "android_tv": client(note="Playback is delegated to the downstream media-server/client stack; no Android TV path was separately verified."),
            "web": client(note="vibeDebrid has a management web UI, while media playback is delegated to Plex/Jellyfin/Infuse."),
        },
        "evidence": [
            ev("The README describes the pipeline as Torrentio/Zilean scraping to Real-Debrid, Zurg/rclone mounting, symlink creation, and Plex/Jellyfin library integration.", "https://github.com/vibeMonarch/vibeDebrid/blob/main/README.md")
        ],
        "verified_at": TODAY,
    },
    {
        "id": "zurg",
        "name": "Zurg",
        "repository": "debridmediamanager/zurg-public",
        "description": "Real-Debrid WebDAV streaming backend that presents a Debrid torrent library to Infuse directly or to media servers through rclone, with on-demand repair of dead links.",
        "architecture": "streaming_backend",
        "dependency": "independent",
        "aiostreams": {
            "state": "unconfirmed",
            "note": "No current first-party AIOStreams integration was confirmed for the public stable path during this survey.",
            "evidence": [],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["Real-Debrid"],
            "usenet": "unknown",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="The README names Infuse as a direct WebDAV consumer, but a tvOS-specific statement was not separately verified for this record."),
            "android_tv": client(note="No Android TV-specific playback path was verified for this record."),
            "web": client(note="Zurg has a web dashboard/config surface, but browser media playback was not verified as a client path."),
        },
        "evidence": [
            ev("The official public README describes Zurg as a self-hosted Real-Debrid WebDAV server for Infuse and rclone-mounted media-server libraries, with on-demand repair.", "https://github.com/debridmediamanager/zurg-public/blob/main/README.md"),
            ev("The README identifies v1.0.0 as the documented public stable release and separately describes sponsor-only nightlies with additional backends; those gated nightly capabilities are not promoted into this stable record.", "https://github.com/debridmediamanager/zurg-public/blob/main/README.md"),
        ],
        "verified_at": TODAY,
    },
    {
        "id": "altmount",
        "name": "AltMount",
        "repository": "javi11/altmount",
        "description": "Usenet/NZB-backed WebDAV streaming backend with a built-in Stremio addon and APIs for handing resolved NZBs to the streaming layer.",
        "architecture": "streaming_backend",
        "dependency": "independent",
        "aiostreams": {
            "state": "plugin_or_bridge",
            "note": "AltMount is independently usable, while its first-party Stremio documentation explicitly describes an AIOStreams/proxy handoff pattern for NZB streams.",
            "evidence": [
                ev("AltMount's official Stremio documentation includes an explicit 'AIOStreams / proxy example' for handing an NZB and Stremio episode id to AltMount.", "https://github.com/javi11/altmount/blob/main/docs/docs/3.%20Configuration/stremio.md", "official_docs")
            ],
        },
        "stremio_protocol": "yes",
        "sources": {
            "debrid": "unknown",
            "debrid_providers": [],
            "usenet": "yes",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="No Apple TV-specific playback path was verified for this record."),
            "android_tv": client(note="No Android TV-specific playback path was verified for this record."),
            "web": client(note="AltMount provides a configuration/admin web UI; browser media playback was not verified as a first-party client path."),
        },
        "evidence": [
            ev("The README describes AltMount as a WebDAV server backed by NZB/Usenet.", "https://github.com/javi11/altmount/blob/main/README.md"),
            ev("The first-party Stremio documentation describes a built-in addon that searches Prowlarr and returns Usenet stream URLs, plus a manual NZB-to-stream API.", "https://github.com/javi11/altmount/blob/main/docs/docs/3.%20Configuration/stremio.md", "official_docs"),
        ],
        "verified_at": TODAY,
    },
    {
        "id": "nzbdav",
        "name": "NzbDAV",
        "repository": "nzbdav-dev/nzbdav",
        "description": "Usenet streaming backend that mounts NZB documents as a seekable WebDAV virtual filesystem and exposes a SABnzbd-compatible automation API for media-server stacks.",
        "architecture": "streaming_backend",
        "dependency": "independent",
        "aiostreams": {
            "state": "plugin_or_bridge",
            "note": "NzbDAV works independently for WebDAV/Arr workflows; its current first-party setup guide also documents an on-demand AIOStreams integration path.",
            "evidence": [
                ev("The official setup guide documents Stremio via AIOStreams: AIOStreams searches Newznab, sends the NZB to NzbDAV, and exposes a streamable URL.", "https://github.com/nzbdav-dev/nzbdav/blob/main/docs/setup-guide.md", "official_docs")
            ],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "unknown",
            "debrid_providers": [],
            "usenet": "yes",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="Playback is exposed through WebDAV/media-server integrations; no Apple TV-specific client path was verified for this record."),
            "android_tv": client(note="Playback is exposed through WebDAV/media-server integrations; no Android TV-specific client path was verified for this record."),
            "web": client(note="NzbDAV has an administration/DAV UI, but a browser playback client was not verified for this record."),
        },
        "evidence": [
            ev("The README describes seekable NZB/Usenet WebDAV streaming, a SABnzbd-compatible API, and Plex/Jellyfin integration without full local downloads.", "https://github.com/nzbdav-dev/nzbdav/blob/main/README.md"),
            ev("The setup guide separately documents Arr/media-server and AIOStreams on-demand flows.", "https://github.com/nzbdav-dev/nzbdav/blob/main/docs/setup-guide.md", "official_docs"),
        ],
        "verified_at": TODAY,
    },
    {
        "id": "infinidysk",
        "name": "InfiniDysk",
        "repository": "infinidysk/infinidysk",
        "homepage": "https://www.infinidysk.com/",
        "description": "NzbDAV-derived Usenet streaming backend combining WebDAV, SABnzbd-compatible automation, Newznab search, and resilient direct NNTP streaming for media-server libraries.",
        "architecture": "streaming_backend",
        "dependency": "independent",
        "aiostreams": {
            "state": "plugin_or_bridge",
            "note": "InfiniDysk works independently as a WebDAV/SAB backend, while its first-party README explicitly lists Stremio through AIOStreams as a supported integration path.",
            "evidence": [
                ev("The official README's integration documentation explicitly lists Stremio through AIOStreams.", "https://github.com/infinidysk/infinidysk/blob/main/README.md")
            ],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "unknown",
            "debrid_providers": [],
            "usenet": "yes",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="Playback is exposed through WebDAV/media-server integrations; no Apple TV-specific path was verified for this record."),
            "android_tv": client(note="Playback is exposed through WebDAV/media-server integrations; no Android TV-specific path was verified for this record."),
            "web": client(note="InfiniDysk ships an operations/admin frontend; browser media playback was not verified as a first-party client path."),
        },
        "evidence": [
            ev("The README describes InfiniDysk as a Usenet WebDAV/SAB backend that streams NZBs without downloading full media first and integrates with Plex, Emby, Jellyfin and other WebDAV consumers.", "https://github.com/infinidysk/infinidysk/blob/main/README.md"),
            ev("The README describes InfiniDysk as a maintained fork/drop-in upgrade from NzbDAV while documenting the two projects' migration relationship.", "https://github.com/infinidysk/infinidysk/blob/main/README.md"),
        ],
        "verified_at": TODAY,
    },
    {
        "id": "davdebrid",
        "name": "DavDebrid",
        "repository": "arvida42/davdebrid",
        "description": "Debrid-Link WebDAV streaming backend that organizes provider media into movie/show folders for rclone-mounted Plex and related media-server libraries.",
        "architecture": "streaming_backend",
        "dependency": "independent",
        "aiostreams": {
            "state": "unconfirmed",
            "note": "No current first-party AIOStreams integration was confirmed during this survey.",
            "evidence": [],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["Debrid-Link"],
            "usenet": "unknown",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="No Apple TV-specific playback path was verified for this record."),
            "android_tv": client(note="No Android TV-specific playback path was verified for this record."),
            "web": client(note="DavDebrid exposes WebDAV rather than a verified browser playback client."),
        },
        "evidence": [
            ev("The current first-party README describes DavDebrid as a self-hosted WebDAV server for Debrid-Link with automatic media organization and Plex/rclone integration.", "https://github.com/arvida42/davdebrid/blob/main/README.md")
        ],
        "verified_at": TODAY,
    },
    {
        "id": "stremthru",
        "name": "StremThru",
        "repository": "MunifTanjim/stremthru",
        "description": "Stremio-oriented streaming proxy/backend that abstracts multiple Debrid stores, proxies byte-range media content, and can route store traffic through HTTP(S) proxies.",
        "architecture": "streaming_backend",
        "dependency": "independent",
        "aiostreams": {
            "state": "unconfirmed",
            "note": "No first-party StremThru documentation was found that establishes AIOStreams as a consuming integration; downstream projects may use both, but that is not promoted here.",
            "evidence": [],
        },
        "stremio_protocol": "yes",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["AllDebrid", "Debrider", "Debrid-Link", "EasyDebrid", "Offcloud", "PikPak", "Premiumize", "RealDebrid", "TorBox", "Torrin"],
            "usenet": "unknown",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="StremThru is a server-side Stremio companion; no Apple TV-specific client path was verified for this record."),
            "android_tv": client(note="StremThru is a server-side Stremio companion; no Android TV-specific client path was verified for this record."),
            "web": client(note="No first-party browser playback client was verified for this record."),
        },
        "evidence": [
            ev("The README describes StremThru as a Stremio companion with HTTP(S) proxying, byte serving, store-content proxying, and integrations for the listed Debrid/cloud stores.", "https://github.com/MunifTanjim/stremthru/blob/main/README.md")
        ],
        "verified_at": TODAY,
    },
    {
        "id": "warpbox",
        "name": "Warpbox",
        "repository": "mainlink0435/warpbox",
        "description": "TorBox-specific WebDAV proxy that caches metadata and CDN URLs, throttles provider API calls, and serves media-server byte-range reads through rclone-mounted libraries.",
        "architecture": "streaming_backend",
        "dependency": "independent",
        "aiostreams": {
            "state": "unconfirmed",
            "note": "No current first-party AIOStreams integration was confirmed during this survey.",
            "evidence": [],
        },
        "stremio_protocol": "unknown",
        "sources": {
            "debrid": "yes",
            "debrid_providers": ["TorBox"],
            "usenet": "unknown",
            "local_media": "unknown",
        },
        "api": {"jellyfin_compatible": "unknown"},
        "clients": {
            "apple_tv": client(note="The project documents Infuse setup through its media-server guide, but a tvOS-specific statement was not separately verified for this record."),
            "android_tv": client(note="No Android TV-specific playback path was verified for this record."),
            "web": client(note="Warpbox exposes WebDAV rather than a verified browser playback client."),
        },
        "evidence": [
            ev("The README describes Warpbox as a TorBox WebDAV proxy that caches metadata/CDN links, rate-limits TorBox API access, and sits between rclone/media servers and TorBox.", "https://github.com/mainlink0435/warpbox/blob/main/README.md"),
            ev("The README points to first-party setup documentation for Plex, Jellyfin, Emby and Infuse consumers.", "https://github.com/mainlink0435/warpbox/blob/main/README.md"),
        ],
        "verified_at": TODAY,
    },
]

with DATA.open("r", encoding="utf-8") as handle:
    doc = json.load(handle)

existing_ids = {project["id"] for project in doc["projects"]}
for project in projects_to_add:
    if project["id"] not in existing_ids:
        doc["projects"].append(project)
        existing_ids.add(project["id"])

with DATA.open("w", encoding="utf-8") as handle:
    json.dump(doc, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
