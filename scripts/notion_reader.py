"""Notion에서 지정한 날짜에 AI가 수집한 자료를 읽는다."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from .settings import NotionSettings, get_notion_settings
except ImportError:  # 파일을 직접 실행할 때 사용
    from settings import NotionSettings, get_notion_settings


NOTION_VERSION = "2026-03-11"
NOTION_QUERY_URL = "https://api.notion.com/v1/data_sources/{data_source_id}/query"
DEFAULT_TIMEZONE = "Asia/Seoul"
KOREA_TIMEZONE = timezone(timedelta(hours=9), name="Asia/Seoul")


class NotionReadError(RuntimeError):
    """Notion 자료를 읽지 못했을 때 발생한다."""


def _plain_text(items: list[dict[str, Any]]) -> str:
    return "".join(str(item.get("plain_text", "")) for item in items).strip()


def _property_text(properties: dict[str, Any], name: str, kind: str) -> str:
    value = properties.get(name, {})
    return _plain_text(value.get(kind, []))


def _multi_select(properties: dict[str, Any], name: str) -> list[str]:
    value = properties.get(name, {})
    return [
        str(item.get("name", "")).strip()
        for item in value.get("multi_select", [])
        if str(item.get("name", "")).strip()
    ]


def page_to_record(page: dict[str, Any]) -> dict[str, Any]:
    """Notion 페이지 응답에서 Slack 브리핑에 필요한 값만 추린다."""

    properties = page.get("properties", {})
    return {
        "title": _property_text(properties, "자료명", "title") or "제목 없음",
        "summary": _property_text(properties, "핵심 요약", "rich_text"),
        "roles": _multi_select(properties, "관련 직무"),
        "work_areas": _multi_select(properties, "업무 영역"),
        "source_url": str(properties.get("원문 링크", {}).get("url") or ""),
        "notion_url": str(page.get("url") or ""),
        "created_time": str(page.get("created_time") or ""),
    }


def get_timezone(timezone_name: str):
    """Windows에 시간대 데이터가 없어도 한국 시간은 항상 계산한다."""

    if timezone_name == DEFAULT_TIMEZONE:
        return KOREA_TIMEZONE
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise NotionReadError(f"알 수 없는 시간대입니다: {timezone_name}") from exc


def _utc_window(target_date: date, timezone_name: str) -> tuple[str, str]:
    local_timezone = get_timezone(timezone_name)

    start = datetime.combine(target_date, time.min, local_timezone)
    end = start + timedelta(days=1)
    return (
        start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        end.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    )


def query_ai_collected_pages(
    target_date: date,
    *,
    timezone_name: str = DEFAULT_TIMEZONE,
    settings: NotionSettings | None = None,
) -> list[dict[str, Any]]:
    """해당 날짜에 생성되고 `수집 경로=AI 서칭`인 페이지를 모두 읽는다."""

    notion = settings or get_notion_settings()
    if not notion.is_configured:
        raise NotionReadError(
            "NOTION_API_KEY와 NOTION_DATA_SOURCE_ID를 모두 설정해 주세요."
        )

    start_utc, end_utc = _utc_window(target_date, timezone_name)
    url = NOTION_QUERY_URL.format(data_source_id=notion.data_source_id)
    headers = {
        "Authorization": f"Bearer {notion.api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json; charset=utf-8",
    }
    base_payload: dict[str, Any] = {
        "filter": {
            "and": [
                {
                    "timestamp": "created_time",
                    "created_time": {"on_or_after": start_utc},
                },
                {
                    "timestamp": "created_time",
                    "created_time": {"before": end_utc},
                },
                {
                    "property": "수집 경로",
                    "select": {"equals": "AI 서칭"},
                },
            ]
        },
        "sorts": [{"timestamp": "created_time", "direction": "ascending"}],
        "page_size": 100,
    }

    pages: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        payload = dict(base_payload)
        if cursor:
            payload["start_cursor"] = cursor
        request = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise NotionReadError(f"Notion 조회 실패: HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise NotionReadError("Notion 서버와 통신하지 못했습니다.") from exc

        pages.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
        if not cursor:
            raise NotionReadError("Notion 페이지 이동 정보가 올바르지 않습니다.")

    return [page_to_record(page) for page in pages]
