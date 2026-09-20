"""표준 입력으로 받은 브리핑을 설정된 Slack 채널에 전송한다."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

try:
    from .settings import get_slack_settings
except ImportError:  # 파일을 직접 실행할 때 사용
    from settings import get_slack_settings


SLACK_POST_MESSAGE_URL = "https://slack.com/api/chat.postMessage"


class SlackSendError(RuntimeError):
    """Slack API가 메시지를 보내지 못했을 때 발생한다."""


def post_message(message: str) -> dict:
    settings = get_slack_settings()
    if not settings.is_configured:
        raise SlackSendError(
            ".env의 SLACK_BOT_TOKEN과 SLACK_CHANNEL_ID를 모두 입력해 주세요."
        )
    if not message.strip():
        raise SlackSendError("보낼 메시지가 비어 있습니다.")

    body = json.dumps(
        {"channel": settings.channel_id, "text": message},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        SLACK_POST_MESSAGE_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {settings.bot_token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise SlackSendError("Slack 서버와 통신하지 못했습니다.") from exc

    if not result.get("ok"):
        error_code = result.get("error", "unknown_error")
        raise SlackSendError(f"Slack 전송 실패: {error_code}")
    return result


def main() -> int:
    message = sys.stdin.buffer.read().decode("utf-8")
    try:
        result = post_message(message)
    except SlackSendError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"SLACK_SENT=True channel={result.get('channel', '')} ts={result.get('ts', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
