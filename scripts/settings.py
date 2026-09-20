"""프로젝트 루트의 .env 파일에서 실행 설정을 읽는다."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PATH = PROJECT_ROOT / ".env"


def load_env_file(path: Path = DEFAULT_ENV_PATH) -> None:
    """간단한 KEY=VALUE 형식의 설정을 환경변수로 불러온다.

    이미 운영체제에 같은 환경변수가 있으면 그 값을 우선한다.
    """

    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class SlackSettings:
    bot_token: str
    channel_id: str

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token and self.channel_id)


def get_slack_settings(path: Path = DEFAULT_ENV_PATH) -> SlackSettings:
    """Slack 전송에 필요한 두 설정값을 반환한다."""

    load_env_file(path)
    return SlackSettings(
        bot_token=os.getenv("SLACK_BOT_TOKEN", "").strip(),
        channel_id=os.getenv("SLACK_CHANNEL_ID", "").strip(),
    )
