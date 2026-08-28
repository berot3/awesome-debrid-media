# Definitions

This project separates architecture, compatibility, and client availability so that one green checkmark does not hide important differences.

## AIOStreams support

### `explicit`
The project explicitly implements or documents AIOStreams support.

This may be a dedicated provider, scraper, plugin, configuration path, or first-party documentation naming AIOStreams.

### `stremio_protocol`
The project implements generic Stremio-addon support and there is evidence that AIOStreams is usable through that protocol.

Do not use this state merely because AIOStreams itself implements the Stremio protocol. The consuming project's implementation and compatibility must be evidenced.

### `plugin_or_bridge`
AIOStreams works through an optional plugin, companion, bridge, or other integration that is not intrinsic to the core project.

### `unconfirmed`
The project is relevant to the comparison, but current first-party evidence is insufficient to classify AIOStreams support positively or negatively.

`unconfirmed` is the correct state when searches find nothing conclusive.

### `none`
First-party AIOStreams support is explicitly absent, unsupported, or declined, and there is evidence for that conclusion.

Do not use `none` merely because no integration was found.

### `scope_conflict`
The capability required for an AIOStreams-style remote-stream integration conflicts with documented product direction or permanent project non-goals.

This is stronger than `none`. It requires durable evidence describing the scope conflict.

## Architecture

### `full_media_server`
A self-hosted system that provides a media-server experience including library/discovery and playback-serving responsibilities.

### `streaming_backend`
A server-side system primarily responsible for discovery, stream resolution, and/or serving streams to clients, without necessarily being a traditional library-centric media server.

### `jellyfin_compatible_server`
An independent server or backend that intentionally exposes enough Jellyfin-compatible API behavior for Jellyfin ecosystem clients.

### `bridge`
A server-side compatibility layer that translates or exposes one ecosystem through another API/client path.

### `media_automation_vfs`
A system whose primary role is media acquisition/automation and virtual filesystem presentation to another media server.

### `media_server_plugin`
A plugin that extends an existing media server and cannot function as the primary server by itself.

### `other`
Relevant server-side architecture that does not fit the above categories. Use sparingly and explain in the project description.

## Capability values

General capability fields use:

- `yes` — confirmed supported;
- `no` — confirmed unsupported;
- `unknown` — insufficient evidence.

Do not silently convert `unknown` to `no`.

## Media-server dependency

- `independent` — can provide its intended server-side function without Jellyfin/Plex/Emby as the host media server.
- `requires_jellyfin` — requires Jellyfin.
- `requires_plex` — requires Plex.
- `requires_emby` — requires Emby.
- `requires_media_server` — requires an external media server, with more than one supported option or no single fixed host.
- `plugin_for_jellyfin` — specifically a Jellyfin plugin rather than an independent server.
- `other` — another documented dependency model.
- `unknown` — not yet established.

## Client availability

Client/platform states are separate from source-code existence:

- `released_first_party` — an installable first-party release is publicly available through the documented distribution path;
- `source_only_first_party` — first-party client source exists, but no public installable release was verified;
- `compatible_third_party` — the backend is intended to work through a third-party client/protocol;
- `unconfirmed` — client support is unclear;
- `none` — support is explicitly absent.

For Apple TV, do not label a project `released_first_party` merely because an iOS/tvOS code target exists.

## Evidence source types

Evidence entries use one of:

- `official_docs`
- `source_code`
- `readme`
- `issue_pr`
- `release`
- `maintainer`
- `community`

See `methodology.md` for source priority and freshness rules.
