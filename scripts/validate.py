#!/usr/bin/env python3
"""Validate the curated Awesome Debrid Media project dataset."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "projects.json"

ARCHITECTURES = {
    "full_media_server",
    "streaming_backend",
    "jellyfin_compatible_server",
    "bridge",
    "media_automation_vfs",
    "media_server_plugin",
    "other",
}
DEPENDENCIES = {
    "independent",
    "requires_jellyfin",
    "requires_plex",
    "requires_emby",
    "requires_media_server",
    "plugin_for_jellyfin",
    "other",
    "unknown",
}
AIO_STATES = {
    "explicit",
    "stremio_protocol",
    "plugin_or_bridge",
    "unconfirmed",
    "none",
    "scope_conflict",
}
CAPABILITY_VALUES = {"yes", "no", "unknown"}
CLIENT_STATES = {
    "released_first_party",
    "source_only_first_party",
    "compatible_third_party",
    "unconfirmed",
    "none",
}
EVIDENCE_TYPES = {
    "official_docs",
    "source_code",
    "readme",
    "issue_pr",
    "release",
    "maintainer",
    "community",
}
FORBIDDEN_VOLATILE_FIELDS = {
    "stars",
    "stargazers_count",
    "forks",
    "forks_count",
    "pushed_at",
    "open_issues",
    "open_issues_count",
    "archived",
    "latest_release",
    "latest_release_at",
}
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def is_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_iso_date(value: object, field: str) -> None:
    require(isinstance(value, str), f"{field} must be a YYYY-MM-DD string")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"{field} must be a valid YYYY-MM-DD date") from exc


def find_forbidden_keys(value: object, path: str = "root") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_VOLATILE_FIELDS:
                found.append(child_path)
            found.extend(find_forbidden_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_forbidden_keys(child, f"{path}[{index}]"))
    return found


def validate_evidence(item: object, path: str) -> None:
    require(isinstance(item, dict), f"{path} must be an object")
    for field in ("claim", "url", "source_type", "checked_at"):
        require(field in item, f"{path}.{field} is required")
    require(isinstance(item["claim"], str) and item["claim"].strip(), f"{path}.claim must be non-empty")
    require(is_http_url(item["url"]), f"{path}.url must be an http(s) URL")
    require(item["source_type"] in EVIDENCE_TYPES, f"{path}.source_type has an invalid value")
    validate_iso_date(item["checked_at"], f"{path}.checked_at")


def validate_evidence_list(value: object, path: str) -> None:
    require(isinstance(value, list), f"{path} must be an array")
    for index, item in enumerate(value):
        validate_evidence(item, f"{path}[{index}]")


def validate_client(client: object, path: str) -> None:
    require(isinstance(client, dict), f"{path} must be an object")
    for field in ("state", "note", "evidence"):
        require(field in client, f"{path}.{field} is required")
    require(client["state"] in CLIENT_STATES, f"{path}.state has an invalid value")
    require(isinstance(client["note"], str), f"{path}.note must be a string")
    validate_evidence_list(client["evidence"], f"{path}.evidence")
    if client["state"] in {"released_first_party", "source_only_first_party", "compatible_third_party", "none"}:
        require(client["evidence"], f"{path}.evidence is required for state {client['state']}")


def validate_project(project: object, index: int) -> str:
    path = f"projects[{index}]"
    require(isinstance(project, dict), f"{path} must be an object")

    required = {
        "id",
        "name",
        "repository",
        "description",
        "architecture",
        "dependency",
        "aiostreams",
        "stremio_protocol",
        "sources",
        "api",
        "clients",
        "evidence",
        "verified_at",
    }
    missing = sorted(required - project.keys())
    require(not missing, f"{path} is missing required fields: {', '.join(missing)}")

    require(isinstance(project["id"], str) and ID_RE.fullmatch(project["id"]), f"{path}.id must be kebab-case")
    require(isinstance(project["name"], str) and project["name"].strip(), f"{path}.name must be non-empty")
    require(isinstance(project["repository"], str) and REPO_RE.fullmatch(project["repository"]), f"{path}.repository must be owner/repo")
    require(isinstance(project["description"], str) and project["description"].strip(), f"{path}.description must be non-empty")
    require(project["architecture"] in ARCHITECTURES, f"{path}.architecture has an invalid value")
    require(project["dependency"] in DEPENDENCIES, f"{path}.dependency has an invalid value")

    if "homepage" in project and project["homepage"] is not None:
        require(is_http_url(project["homepage"]), f"{path}.homepage must be an http(s) URL")

    aio = project["aiostreams"]
    require(isinstance(aio, dict), f"{path}.aiostreams must be an object")
    for field in ("state", "note", "evidence"):
        require(field in aio, f"{path}.aiostreams.{field} is required")
    require(aio["state"] in AIO_STATES, f"{path}.aiostreams.state has an invalid value")
    require(isinstance(aio["note"], str), f"{path}.aiostreams.note must be a string")
    validate_evidence_list(aio["evidence"], f"{path}.aiostreams.evidence")
    if aio["state"] != "unconfirmed":
        require(aio["evidence"], f"{path}.aiostreams.evidence is required for state {aio['state']}")

    require(project["stremio_protocol"] in CAPABILITY_VALUES, f"{path}.stremio_protocol has an invalid value")

    sources = project["sources"]
    require(isinstance(sources, dict), f"{path}.sources must be an object")
    for field in ("debrid", "debrid_providers", "usenet", "local_media"):
        require(field in sources, f"{path}.sources.{field} is required")
    for field in ("debrid", "usenet", "local_media"):
        require(sources[field] in CAPABILITY_VALUES, f"{path}.sources.{field} has an invalid value")
    require(isinstance(sources["debrid_providers"], list), f"{path}.sources.debrid_providers must be an array")
    require(all(isinstance(provider, str) and provider.strip() for provider in sources["debrid_providers"]), f"{path}.sources.debrid_providers must contain non-empty strings")
    require(len(sources["debrid_providers"]) == len(set(sources["debrid_providers"])), f"{path}.sources.debrid_providers must not contain duplicates")

    api = project["api"]
    require(isinstance(api, dict), f"{path}.api must be an object")
    require("jellyfin_compatible" in api, f"{path}.api.jellyfin_compatible is required")
    require(api["jellyfin_compatible"] in CAPABILITY_VALUES, f"{path}.api.jellyfin_compatible has an invalid value")

    clients = project["clients"]
    require(isinstance(clients, dict), f"{path}.clients must be an object")
    for platform in ("apple_tv", "android_tv", "web"):
        require(platform in clients, f"{path}.clients.{platform} is required")
        validate_client(clients[platform], f"{path}.clients.{platform}")

    validate_evidence_list(project["evidence"], f"{path}.evidence")
    validate_iso_date(project["verified_at"], f"{path}.verified_at")

    forbidden = find_forbidden_keys(project, path)
    require(not forbidden, f"{path} contains volatile fields that must be build-time only: {', '.join(forbidden)}")

    return project["id"]


def main() -> int:
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        require(isinstance(data, dict), "dataset root must be an object")
        require(data.get("schema_version") == 1, "schema_version must be 1")
        require(isinstance(data.get("projects"), list), "projects must be an array")

        ids = [validate_project(project, index) for index, project in enumerate(data["projects"])]
        require(len(ids) == len(set(ids)), "project ids must be unique")

    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"validation passed: {len(data['projects'])} project(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
