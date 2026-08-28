# Project data schema

`data/projects.json` is the manually curated source of truth.

The root object has:

```json
{
  "schema_version": 1,
  "projects": []
}
```

Each project record must use the following shape.

```json
{
  "id": "example-project",
  "name": "Example Project",
  "repository": "owner/repo",
  "homepage": "https://example.org/",
  "description": "Short factual description.",
  "architecture": "full_media_server",
  "dependency": "independent",
  "aiostreams": {
    "state": "explicit",
    "note": "Short precise explanation.",
    "evidence": [
      {
        "claim": "Official README names AIOStreams as a supported source.",
        "url": "https://github.com/owner/repo/blob/main/README.md",
        "source_type": "readme",
        "checked_at": "2026-08-28"
      }
    ]
  },
  "stremio_protocol": "yes",
  "sources": {
    "debrid": "yes",
    "debrid_providers": ["TorBox"],
    "usenet": "unknown",
    "local_media": "yes"
  },
  "api": {
    "jellyfin_compatible": "no"
  },
  "clients": {
    "apple_tv": {
      "state": "released_first_party",
      "note": "Public TestFlight build.",
      "evidence": []
    },
    "android_tv": {
      "state": "released_first_party",
      "note": "Public APK release.",
      "evidence": []
    },
    "web": {
      "state": "released_first_party",
      "note": "Built-in web client.",
      "evidence": []
    }
  },
  "evidence": [],
  "verified_at": "2026-08-28"
}
```

## Required fields

Every record requires:

- `id`
- `name`
- `repository`
- `description`
- `architecture`
- `dependency`
- `aiostreams`
- `stremio_protocol`
- `sources`
- `api`
- `clients`
- `evidence`
- `verified_at`

`homepage` is optional.

## Enumerations

### `architecture`

- `full_media_server`
- `streaming_backend`
- `jellyfin_compatible_server`
- `bridge`
- `media_automation_vfs`
- `media_server_plugin`
- `other`

### `dependency`

- `independent`
- `requires_jellyfin`
- `requires_plex`
- `requires_emby`
- `requires_media_server`
- `plugin_for_jellyfin`
- `other`
- `unknown`

### `aiostreams.state`

- `explicit`
- `stremio_protocol`
- `plugin_or_bridge`
- `unconfirmed`
- `none`
- `scope_conflict`

All states except `unconfirmed` require at least one AIOStreams evidence entry.

### General capability values

- `yes`
- `no`
- `unknown`

Used by `stremio_protocol`, `sources.debrid`, `sources.usenet`, `sources.local_media`, and `api.jellyfin_compatible`.

### Client state

- `released_first_party`
- `source_only_first_party`
- `compatible_third_party`
- `unconfirmed`
- `none`

### Evidence source type

- `official_docs`
- `source_code`
- `readme`
- `issue_pr`
- `release`
- `maintainer`
- `community`

## Evidence objects

Every evidence entry contains:

- `claim` — what the source establishes;
- `url` — durable source URL;
- `source_type` — one of the allowed evidence types;
- `checked_at` — the date this source was inspected.

Evidence should support the actual field being classified. A generic project README is not sufficient evidence for every capability in the record.

## Volatile data is forbidden

Do not manually store:

- GitHub stars;
- forks;
- last push timestamps;
- open issue counts;
- archival state;
- latest release date.

These values belong to build-time enrichment, not the curated dataset.
