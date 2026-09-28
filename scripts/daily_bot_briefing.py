"""오늘의 Notion 자료를 읽어 Slack 봇으로 한 번 전송한다."""

from __future__ import annotations

import argparse
from datetime import date, datetime
try:
    from .briefing_formatter import format_daily_briefing
    from .notion_reader import (
        DEFAULT_TIMEZONE,
        NotionReadError,
        get_timezone,
        query_ai_collected_pages,
    )
    from .settings import get_slack_settings
    from .slack_sender import SlackSendError, post_message
except ImportError:  # 파일을 직접 실행할 때 사용
    from briefing_formatter import format_daily_briefing
    from notion_reader import (
        DEFAULT_TIMEZONE,
        NotionReadError,
        get_timezone,
        query_ai_collected_pages,
    )
    from settings import get_slack_settings
    from slack_sender import SlackSendError, post_message


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("날짜는 YYYY-MM-DD 형식이어야 합니다.") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=_parse_date, help="조회할 한국 날짜(YYYY-MM-DD)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Slack으로 보내지 않고 완성 메시지만 출력",
    )
    args = parser.parse_args()

    target_date = args.date or datetime.now(get_timezone(DEFAULT_TIMEZONE)).date()
    slack = get_slack_settings()
    try:
        records = query_ai_collected_pages(target_date)
        message = format_daily_briefing(
            records,
            target_date,
            mention_user_id=slack.mention_user_id,
        )
        if args.dry_run:
            print(message)
            return 0
        result = post_message(message)
    except (NotionReadError, SlackSendError) as exc:
        print(str(exc))
        return 1

    print(
        "DAILY_BRIEFING_SENT=True "
        f"date={target_date.isoformat()} count={len(records)} "
        f"channel={result.get('channel', '')} ts={result.get('ts', '')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
