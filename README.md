# 산업·직무 인사이트 아카이빙 시스템

유통/커머스/리테일 산업과 MD·HR 직무의 공개 자료를 찾아, 취업 준비에 다시 활용할 핵심만 Notion에 축적하는 개인용 프로토타입입니다.

## 해결하려는 문제

뉴스와 기업 콘텐츠를 많이 모으는 것보다 다음 흐름을 반복할 수 있도록 만드는 것이 목표입니다.

> 자료 발견 → 관련성 판단 → 핵심 정리 → 산업·직무 연결 → Notion 저장

## 현재 구현 범위

- `직무 공부`와 `산업·기업 동향` 목적 구분
- 채용공고와 단순 홍보·행사 자료 제외
- MD·HR의 실제 업무, 판단과 고민이 드러나는 자료 우선
- 핵심 내용, 산업·직무 연결, 취업 준비 관점 정리
- 원문 URL 정규화와 로컬 인덱스를 이용한 중복 확인
- Codex의 Notion 연결을 이용한 수동 저장과 생성 페이지 확인

뉴스 수집과 Notion 저장은 기존 웹 ChatGPT 예약이 담당합니다. 이 브랜치는 별도 플러그인이나 OpenAI API 없이, GitHub Actions가 Notion의 당일 저장 자료를 읽어 Slack 봇으로 전송하는 기능을 추가합니다.

## 핵심 원칙

- 모든 항목을 억지로 채우지 않습니다.
- 산업·직무와 직접 관련된 내용만 연결합니다.
- 원문에 없는 성과나 맥락을 추측하지 않습니다.
- 나중에 다시 봤을 때 기억해야 할 내용만 짧게 남깁니다.
- 성과, 별도 인사이트와 추가 질문은 취업 준비 가치가 분명할 때만 선택적으로 작성합니다.

상세 기준은 [자료 수집·정리 기준](docs/collection-policy.md), 제품 범위는 [PRD](PRD.md)를 참고하세요.

## 프로젝트 구조

```text
.
├─ README.md
├─ PRD.md
├─ .gitignore
├─ data/
│  ├─ archive-index.example.jsonl  # 공개용 예시
│  └─ archive-index.jsonl          # 개인용 실제 기록, Git 제외
├─ docs/
│  ├─ collection-policy.md
│  └─ notion-schema.md
├─ .github/workflows/
│  └─ daily-slack-bot.yml        # 매일 오전 9시 봇 브리핑
├─ scripts/
│  ├─ archive_index.py
│  ├─ notion_reader.py
│  ├─ briefing_formatter.py
│  ├─ slack_sender.py
│  └─ daily_bot_briefing.py
└─ tests/
   └─ test_*.py
```

## Slack 봇 자동 브리핑

기존 흐름은 유지합니다.

1. 매일 오전 8시 웹 ChatGPT 예약이 뉴스 수집·검수·Notion 저장을 수행합니다.
2. 매일 오전 9시 GitHub Actions가 `수집 경로=AI 서칭`인 당일 자료를 조회합니다.
3. 조회 결과를 한 메시지로 묶어 Slack 봇이 지정 채널에 보냅니다.

이 기능은 OpenAI API를 사용하지 않습니다. Notion 읽기 인증값과 Slack 봇 인증값만 사용합니다. 자동 실행에 필요한 값은 GitHub 저장소의 `Settings → Secrets and variables → Actions`에서 다음 이름의 Repository secret으로 등록합니다.

- `NOTION_API_KEY`
- `NOTION_DATA_SOURCE_ID`
- `SLACK_BOT_TOKEN`
- `SLACK_CHANNEL_ID`
- `SLACK_MENTION_USER_ID` — 선택값, 본인 Slack 사용자 ID

실제 값은 저장소 파일과 대화에 적지 않습니다. Notion 연결에는 대상 데이터 소스 읽기 권한이 필요하며, Slack 앱에는 `chat:write` 권한과 비공개 `#news-briefing` 채널 참여가 필요합니다.

로컬에서 Slack 전송 없이 메시지만 확인할 때는 `.env` 설정 후 다음 명령을 사용합니다.

```powershell
python scripts/daily_bot_briefing.py --dry-run
```

GitHub Actions의 예약 실행은 워크플로 파일이 기본 브랜치에 합쳐진 뒤부터 동작합니다. 첫 실제 전송에 성공하기 전에는 웹 ChatGPT 예약의 기존 Slack 전송 단계를 제거하지 않습니다.

## 중복 확인 도구 사용

Python 3만 있으면 별도 설치 없이 실행할 수 있습니다.

```powershell
python scripts/archive_index.py validate data/archive-index.example.jsonl
python scripts/archive_index.py summary data/archive-index.example.jsonl
python scripts/archive_index.py contains data/archive-index.example.jsonl "https://example.com/article?utm_source=test"
```

전체 시험은 다음 명령으로 실행합니다.

```powershell
python -m unittest discover -s tests -v
```

## Notion 사용 준비

웹 ChatGPT의 뉴스 저장은 계속 연결된 Notion을 사용합니다. 별도 Slack 봇 전송 코드는 같은 DB를 읽기 위해 Notion 내부 통합 인증값을 사용하며, 로컬 시험에서는 `.env`, GitHub 자동 실행에서는 Repository secrets에 보관합니다. 필요한 데이터베이스 속성은 [Notion DB 구조](docs/notion-schema.md)에 정리되어 있습니다.

## 공개 저장소 안전 기준

- 실제 `data/archive-index.jsonl`은 개인 Notion 페이지 주소가 포함되므로 Git에서 제외합니다.
- 공개할 때는 `data/archive-index.example.jsonl`만 사용합니다.
- 비밀번호, Notion 인증값 또는 API 키를 파일에 기록하지 않습니다.
- 향후 `.env`를 사용하더라도 실제 파일은 Git에 포함되지 않습니다.

## 현재 한계

- 웹 ChatGPT 수집이 오전 9시까지 끝나지 않으면 해당 날짜의 봇 브리핑에서 일부 자료가 빠질 수 있습니다.
- Notion에서 직접 수정한 내용과 로컬 인덱스는 자동 동기화되지 않습니다.
- 실제 자료의 요약과 직무 연결은 사용자가 최종 검토해야 합니다.
