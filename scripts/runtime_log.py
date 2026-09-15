#!/usr/bin/env python3
"""Keep lightweight decision and run logs, pruning records older than 90 days."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


RETENTION_DAYS = 90


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def prune_records(records: list[dict], timestamp_field: str, now: datetime) -> list[dict]:
    cutoff = now.astimezone(timezone.utc) - timedelta(days=RETENTION_DAYS)
    kept = []
    for record in records:
        value = record.get(timestamp_field)
        if value and parse_timestamp(value) >= cutoff:
            kept.append(record)
    return kept


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: 올바르지 않은 JSON입니다") from exc
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
    path.write_text(text, encoding="utf-8")


def prune_file(path: Path, timestamp_field: str, now: datetime) -> tuple[int, int]:
    records = read_jsonl(path)
    kept = prune_records(records, timestamp_field, now)
    write_jsonl(path, kept)
    return len(records), len(kept)


def main() -> int:
    parser = argparse.ArgumentParser(description="90일이 지난 가벼운 실행 기록을 정리합니다.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--timestamp-field", default="checked_at")
    args = parser.parse_args()
    try:
        before, after = prune_file(args.path, args.timestamp_field, datetime.now(timezone.utc))
        print(json.dumps({"before": before, "after": after, "removed": before - after}, ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
