# Awesome Debrid Media

A curated, evidence-based comparison of self-hosted media servers, streaming backends, bridges, and media-automation systems for Debrid & Usenet.

**Comparison site:** https://berot3.github.io/awesome-debrid-media/

> The Pages workflow is part of the initial release. Until that release is merged and GitHub Pages is enabled for the repository, the URL above may not be live yet.

## Why this exists

Broad Debrid lists are useful, but they usually do not compare the architecture and client experience of the newer server-side media projects in enough detail. This project focuses on questions such as:

- Does the project support AIOStreams directly, via the Stremio protocol, through a bridge, or not at all?
- Is it a full media server, a streaming backend, a Jellyfin-compatible server, a bridge, plugin, or a VFS/automation layer?
- Does it work independently, or does it require Jellyfin, Plex, Emby, or another media server?
- Which Debrid and Usenet paths are officially supported?
- What is the real Apple TV/tvOS story: first-party release, source-only app, or compatible third-party client?

This is **not** a generic awesome-selfhosted list, and inclusion is **not an endorsement or recommendation**.

## Source of truth

Curated project facts live in [`data/projects.json`](data/projects.json). Generated site output must not become a second independent source of truth.

Volatile GitHub metadata such as stars, forks, last push, and archival status is intentionally kept out of the curated dataset and is resolved during the Pages build.

## AIOStreams classification

The project distinguishes between:

- `explicit` — the project explicitly implements or documents AIOStreams support.
- `stremio_protocol` — generic Stremio-addon support is implemented and AIOStreams compatibility is evidenced through that protocol.
- `plugin_or_bridge` — AIOStreams works through an optional/external integration layer.
- `unconfirmed` — relevant architecture, but current first-party evidence is insufficient.
- `none` — first-party support is explicitly absent or unsupported, with evidence.
- `scope_conflict` — the required remote-stream capability conflicts with documented product direction.

See [`docs/definitions.md`](docs/definitions.md) and [`docs/methodology.md`](docs/methodology.md) for the full semantics and evidence policy.

## Development

The repository intentionally uses a lightweight standard-library Python toolchain.

```bash
python3 scripts/validate.py
python3 scripts/build.py
```

`validate.py` checks the curated dataset and its evidence semantics. `build.py` produces the static site in `dist/`.

To enrich a local build with current public GitHub metadata:

```bash
FETCH_GITHUB_METADATA=1 python3 scripts/build.py
```

The Pages workflow performs this enrichment automatically with the repository's `GITHUB_TOKEN`; volatile metadata is not committed back into the curated data.

## Contributing

Corrections and project suggestions are welcome. Use the repository issue forms or edit `data/projects.json` directly in a pull request and provide evidence for load-bearing claims.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before changing classifications. Agent-based contributors should also read [`AGENTS.md`](AGENTS.md).

## License

This repository uses split permissive licensing by material type:

- implementation/source code is licensed under the **MIT License**;
- the curated dataset and repository-authored documentation/content are dedicated under **CC0 1.0 Universal**.

See [`LICENSE`](LICENSE) for the exact file-level scope and [`LICENSES/`](LICENSES/) for the full license texts. Third-party project names, trademarks, logos, screenshots, linked pages, quotations, and other third-party material are not relicensed merely because this repository references them.

## Related resources

Broader ecosystem lists remain valuable and complementary. In particular, [`debridmediamanager/awesome-debrid`](https://github.com/debridmediamanager/awesome-debrid) covers a much wider Debrid ecosystem than this project intends to duplicate.
