#!/usr/bin/env python3
"""Report curated project records and evidence entries that are due for re-audit.

Freshness is advisory only. An old date means "needs recheck", never that the
underlying claim is false, unsupported, or unconfirmed.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "projects.json"
DEFAULT_THRESHOLD_DAYS = 120


def parse_iso_date(value: object, label: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a YYYY-MM-DD string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a valid YYYY-MM-DD date") from exc


def parse_as_of(value: str) -> date:
    return parse_iso_date(value, "--as-of")


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def iter_evidence(value: object, path: str = "") -> Iterator[tuple[str, dict]]:
    if isinstance(value, dict):
        if {"claim", "url", "checked_at"}.issubset(value):
            yield path, value
            return
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            yield from iter_evidence(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_evidence(child, f"{path}[{index}]")


def due_item(
    *,
    project: dict,
    kind: str,
    path: str,
    checked_date: date,
    as_of: date,
    threshold_days: int,
    claim: str | None = None,
    url: str | None = None,
) -> dict | None:
    age_days = (as_of - checked_date).days
    if age_days < threshold_days:
        return None
    return {
        "project_id": project["id"],
        "project_name": project["name"],
        "kind": kind,
        "path": path,
        "date": checked_date.isoformat(),
        "age_days": age_days,
        "claim": claim,
        "url": url,
    }


def collect_due(data: dict, as_of: date, threshold_days: int) -> list[dict]:
    due: list[dict] = []

    for project in data.get("projects", []):
        verified = parse_iso_date(project.get("verified_at"), f"{project.get('id', '<unknown>')}.verified_at")
        item = due_item(
            project=project,
            kind="project",
            path="verified_at",
            checked_date=verified,
            as_of=as_of,
            threshold_days=threshold_days,
        )
        if item:
            due.append(item)

        for path, evidence in iter_evidence(project):
            checked = parse_iso_date(
                evidence.get("checked_at"),
                f"{project.get('id', '<unknown>')}.{path}.checked_at",
            )
            item = due_item(
                project=project,
                kind="evidence",
                path=path,
                checked_date=checked,
                as_of=as_of,
                threshold_days=threshold_days,
                claim=evidence.get("claim"),
                url=evidence.get("url"),
            )
            if item:
                due.append(item)

    return sorted(due, key=lambda item: (item["project_id"], item["kind"], item["path"]))


def render_text(*, data: dict, due: list[dict], as_of: date, threshold_days: int) -> str:
    lines = [
        "Evidence freshness report",
        f"As of: {as_of.isoformat()} (UTC date)",
        f"Re-audit threshold: {threshold_days} days or older (advisory only)",
        f"Projects scanned: {len(data.get('projects', []))}",
        f"Items due for recheck: {len(due)}",
        "",
    ]

    if not due:
        lines.append("No project records or evidence entries are due for recheck.")
        return "\n".join(lines)

    current_project = None
    for item in due:
        if item["project_id"] != current_project:
            if current_project is not None:
                lines.append("")
            lines.append(f"{item['project_name']} ({item['project_id']})")
            current_project = item["project_id"]

        if item["kind"] == "project":
            lines.append(
                f"  - project verification: {item['date']} ({item['age_days']} days old)"
            )
            continue

        lines.append(
            f"  - evidence: {item['path']} · {item['date']} ({item['age_days']} days old)"
        )
        if item.get("claim"):
            lines.append(f"    claim: {item['claim']}")
        if item.get("url"):
            lines.append(f"    url: {item['url']}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List curated project/evidence dates that are due for advisory re-audit."
    )
    parser.add_argument(
        "--as-of",
        type=parse_as_of,
        default=datetime.now(timezone.utc).date(),
        help="UTC date used for age calculation (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--threshold-days",
        type=positive_int,
        default=DEFAULT_THRESHOLD_DAYS,
        help=f"Age that triggers a re-audit reminder. Default: {DEFAULT_THRESHOLD_DAYS}.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format. Default: text.",
    )
    args = parser.parse_args()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
            raise ValueError("dataset root must contain a projects array")
        due = collect_due(data, args.as_of, args.threshold_days)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"freshness report failed: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(
            json.dumps(
                {
                    "as_of": args.as_of.isoformat(),
                    "threshold_days": args.threshold_days,
                    "advisory_only": True,
                    "projects_scanned": len(data["projects"]),
                    "due_count": len(due),
                    "due": due,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(
            render_text(
                data=data,
                due=due,
                as_of=args.as_of,
                threshold_days=args.threshold_days,
            )
        )

    # Staleness is deliberately advisory. Due items never make this command fail.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
