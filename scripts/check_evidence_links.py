#!/usr/bin/env python3
"""Check curated evidence URLs without changing or reclassifying project facts.

Link health is advisory. A broken or unreachable citation means the evidence
source needs maintenance; it never proves that the cited project claim is false.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "projects.json"
DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRIES = 1
DEFAULT_WORKERS = 8
USER_AGENT = (
    "awesome-debrid-media-evidence-link-check/1.0 "
    "(+https://github.com/berot3/awesome-debrid-media)"
)
CATEGORY_ORDER = ("healthy", "redirect", "missing", "ambiguous", "transient")


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def iter_evidence(value: object, path: str = "") -> Iterator[tuple[str, dict]]:
    if isinstance(value, dict):
        if {"claim", "url"}.issubset(value):
            yield path, value
            return
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            yield from iter_evidence(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_evidence(child, f"{path}[{index}]")


def validate_url(url: object, label: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ValueError(f"{label} must be a non-empty URL string")
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{label} must be an http(s) URL")
    return url


def collect_targets(data: dict) -> list[dict]:
    projects = data.get("projects")
    if not isinstance(projects, list):
        raise ValueError("dataset root must contain a projects array")

    targets: dict[str, dict] = {}
    for project in projects:
        if not isinstance(project, dict):
            raise ValueError("each project must be an object")
        project_id = project.get("id")
        project_name = project.get("name")
        if not isinstance(project_id, str) or not isinstance(project_name, str):
            raise ValueError("each project must contain string id and name values")

        for path, evidence in iter_evidence(project):
            url = validate_url(evidence.get("url"), f"{project_id}.{path}.url")
            reference = {
                "project_id": project_id,
                "project_name": project_name,
                "path": path,
                "claim": evidence.get("claim"),
                "checked_at": evidence.get("checked_at"),
            }
            target = targets.setdefault(url, {"url": url, "references": []})
            target["references"].append(reference)

    return [targets[url] for url in sorted(targets)]


def request_once(url: str, timeout: float) -> tuple[int | None, str, str | None]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
    }

    def perform(method: str) -> tuple[int | None, str, str | None]:
        request_headers = dict(headers)
        if method == "GET":
            request_headers["Range"] = "bytes=0-0"
        request = urllib.request.Request(url, headers=request_headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if method == "GET":
                    response.read(1)
                return response.getcode(), response.geturl(), None
        except urllib.error.HTTPError as exc:
            return exc.code, exc.geturl() or url, str(exc.reason or exc)

    status, final_url, detail = perform("HEAD")
    if status in {405, 501}:
        status, final_url, detail = perform("GET")
    return status, final_url, detail


def classify(status: int | None, original_url: str, final_url: str) -> str:
    if status is None:
        return "transient"
    if 200 <= status < 300:
        return "redirect" if final_url != original_url else "healthy"
    if 300 <= status < 400:
        return "redirect"
    if status in {404, 410}:
        return "missing"
    if status in {401, 403, 429}:
        return "ambiguous"
    if 400 <= status < 500:
        return "ambiguous"
    return "transient"


def check_target(target: dict, timeout: float, retries: int) -> dict:
    url = target["url"]
    attempts = 0
    last: dict | None = None

    while attempts <= retries:
        attempts += 1
        try:
            status, final_url, detail = request_once(url, timeout)
            category = classify(status, url, final_url)
            last = {
                "url": url,
                "final_url": final_url,
                "status": status,
                "category": category,
                "attempts": attempts,
                "detail": detail,
                "references": target["references"],
            }
        except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:
            last = {
                "url": url,
                "final_url": url,
                "status": None,
                "category": "transient",
                "attempts": attempts,
                "detail": str(exc),
                "references": target["references"],
            }

        if last["category"] != "transient" or attempts > retries:
            return last
        time.sleep(min(0.25 * attempts, 1.0))

    assert last is not None
    return last


def collect_results(
    targets: list[dict], timeout: float, retries: int, workers: int
) -> list[dict]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(check_target, target, timeout, retries)
            for target in targets
        ]
        results = [future.result() for future in futures]
    return sorted(results, key=lambda item: item["url"])


def render_text(results: list[dict]) -> str:
    counts = Counter(item["category"] for item in results)
    normal_count = counts["healthy"] + counts["redirect"]
    lines = [
        "Evidence link health report",
        "Advisory only: link health never changes project facts or verification dates.",
        f"Unique evidence URLs scanned: {len(results)}",
        f"Normal/healthy: {normal_count} (healthy {counts['healthy']}, redirects {counts['redirect']})",
        f"Likely missing (404/410): {counts['missing']}",
        f"Access/rate-limit ambiguity: {counts['ambiguous']}",
        f"Transient/network failure: {counts['transient']}",
        "",
    ]

    findings = [item for item in results if item["category"] != "healthy"]
    if not findings:
        lines.append("No redirects or link-health problems detected.")
        return "\n".join(lines)

    for item in findings:
        status = item["status"] if item["status"] is not None else "network"
        lines.append(f"[{item['category']}] {item['url']}")
        lines.append(f"  status: {status} · attempts: {item['attempts']}")
        if item["final_url"] != item["url"]:
            lines.append(f"  final: {item['final_url']}")
        if item.get("detail"):
            lines.append(f"  detail: {item['detail']}")
        for ref in item["references"]:
            claim = f" — {ref['claim']}" if ref.get("claim") else ""
            lines.append(
                f"  evidence: {ref['project_name']} ({ref['project_id']}) · {ref['path']}{claim}"
            )
        lines.append("")

    return "\n".join(lines).rstrip()


def json_payload(results: list[dict]) -> dict:
    counts = Counter(item["category"] for item in results)
    return {
        "advisory_only": True,
        "unique_urls_scanned": len(results),
        "counts": {category: counts[category] for category in CATEGORY_ORDER},
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check curated evidence URLs and report advisory link-health findings."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DATA_FILE,
        help="Dataset path. Defaults to data/projects.json.",
    )
    parser.add_argument(
        "--timeout",
        type=positive_float,
        default=DEFAULT_TIMEOUT,
        help=f"Per-request timeout in seconds. Default: {DEFAULT_TIMEOUT:g}.",
    )
    parser.add_argument(
        "--retries",
        type=nonnegative_int,
        default=DEFAULT_RETRIES,
        help=f"Retries for transient/network failures. Default: {DEFAULT_RETRIES}.",
    )
    parser.add_argument(
        "--workers",
        type=positive_int,
        default=DEFAULT_WORKERS,
        help=f"Maximum concurrent URL checks. Default: {DEFAULT_WORKERS}.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format. Default: text.",
    )
    args = parser.parse_args()

    try:
        with args.data.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("dataset root must be an object")
        targets = collect_targets(data)
        results = collect_results(targets, args.timeout, args.retries, args.workers)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"evidence link check failed: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(json_payload(results), indent=2, ensure_ascii=False))
    else:
        print(render_text(results))

    # External link findings are advisory. Only script/data/config failures return non-zero.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
