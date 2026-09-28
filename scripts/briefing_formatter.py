"""Notion 자료를 Slack에서 읽기 쉬운 데일리 브리핑으로 만든다."""

from __future__ import annotations

from datetime import date
from typing import Any


def _shorten(text: str, limit: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _link(label: str, url: str) -> str:
    return f"<{url}|{label}>" if url else ""


def format_daily_briefing(
    records: list[dict[str, Any]],
    target_date: date,
    *,
    mention_user_id: str = "",
) -> str:
    """Slack mrkdwn 형식의 한 메시지를 만든다."""

    hr_count = sum("HR" in record.get("roles", []) for record in records)
    md_count = sum("MD" in record.get("roles", []) for record in records)
    lines: list[str] = []
    if mention_user_id:
        lines.append(f"<@{mention_user_id}>")
    lines.extend(
        [
            f"*HR·MD 데일리 브리핑 · {target_date.isoformat()}*",
            f"오늘 저장 {len(records)}건 · HR {hr_count}건 · MD {md_count}건",
        ]
    )

    if not records:
        lines.extend(
            [
                "",
                "오늘 새로 저장된 AI 수집 자료가 없습니다.",
                "웹 예약의 실행 결과와 Notion 저장 상태를 확인해 주세요.",
            ]
        )
        return "\n".join(lines)

    for index, record in enumerate(records, start=1):
        labels = list(record.get("roles", [])) + list(record.get("work_areas", []))
        links = [
            value
            for value in (
                _link("원문", str(record.get("source_url", ""))),
                _link("Notion", str(record.get("notion_url", ""))),
            )
            if value
        ]
        lines.extend(["", f"*{index}. {record.get('title', '제목 없음')}*"])
        if labels:
            lines.append(" · ".join(labels))
        summary = _shorten(str(record.get("summary", "")))
        if summary:
            lines.append(summary)
        if links:
            lines.append(" · ".join(links))

    return "\n".join(lines)
