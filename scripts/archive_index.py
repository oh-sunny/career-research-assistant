#!/usr/bin/env python3
"""Inspect the local archive index without querying the whole Notion database."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_KEYS = {"fbclid", "gclid", "igshid", "mc_cid", "mc_eid"}
REQUIRED_FIELDS = {
    "canonical_url",
    "title",
    "purpose",
    "roles",
    "work_areas",
    "notion_page_url",
    "saved_at",
}


def normalize_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    parts = urlsplit(raw_url)
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError(f"올바른 HTTP(S) URL이 아닙니다: {raw_url}")

    scheme = parts.scheme.lower()
    hostname = parts.hostname.lower()
    port = parts.port
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        hostname = f"{hostname}:{port}"
    path = parts.path.rstrip("/") or "/"
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_KEYS
    ]
    query.sort()
    return urlunsplit((scheme, hostname, path, urlencode(query), ""))


def load_index(index_path: Path) -> list[dict]:
    if not index_path.exists():
        return []

    records: list[dict] = []
    for line_number, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{index_path}:{line_number}: 올바르지 않은 JSON입니다: {exc}") from exc

        missing = REQUIRED_FIELDS - record.keys()
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"{index_path}:{line_number}: 필수 필드가 없습니다: {missing_text}")

        record["canonical_url"] = normalize_url(record["canonical_url"])
        records.append(record)
    return records


def build_summary(records: list[dict]) -> dict:
    purposes: Counter[str] = Counter()
    roles: Counter[str] = Counter()
    work_areas: Counter[str] = Counter()
    role_work_areas: Counter[str] = Counter()
    for record in records:
        purposes[record.get("purpose", "미분류")] += 1
        record_roles = record.get("roles", [])
        record_areas = record.get("work_areas", [])
        roles.update(record_roles)
        work_areas.update(record_areas)
        for role in record_roles:
            for area in record_areas:
                role_work_areas[f"{role} / {area}"] += 1
    return {
        "total": len(records),
        "by_purpose": dict(sorted(purposes.items())),
        "by_role": dict(sorted(roles.items())),
        "by_work_area": dict(sorted(work_areas.items())),
        "by_role_and_work_area": dict(sorted(role_work_areas.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="산업·직무 자료 로컬 인덱스를 확인합니다.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    normalize_parser = subparsers.add_parser("normalize", help="URL을 중복 비교용으로 정리합니다.")
    normalize_parser.add_argument("url")

    for command in ("contains", "summary", "validate"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("index", type=Path)
        if command == "contains":
            command_parser.add_argument("url")

    args = parser.parse_args()

    try:
        if args.command == "normalize":
            print(normalize_url(args.url))
            return 0

        records = load_index(args.index)
        if args.command == "contains":
            candidate = normalize_url(args.url)
            matches = [record for record in records if record["canonical_url"] == candidate]
            print(json.dumps({"found": bool(matches), "canonical_url": candidate, "matches": matches}, ensure_ascii=False, indent=2))
            return 0

        canonical_urls = [record["canonical_url"] for record in records]
        duplicate_urls = sorted(url for url, count in Counter(canonical_urls).items() if count > 1)
        if args.command == "validate":
            print(json.dumps({"valid": not duplicate_urls, "records": len(records), "duplicate_urls": duplicate_urls}, ensure_ascii=False, indent=2))
            return 0 if not duplicate_urls else 1

        print(json.dumps(build_summary(records), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
