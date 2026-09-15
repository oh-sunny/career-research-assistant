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

현재 버전은 사용자가 Codex에서 직접 실행하는 프로토타입입니다. 정기 자동 실행과 Slack 전송은 포함하지 않습니다.

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
├─ scripts/
│  └─ archive_index.py
└─ tests/
   └─ test_archive_index.py
```

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

현재 프로토타입은 API 키를 코드에서 직접 사용하는 방식이 아니라, Codex에 연결된 Notion을 사용합니다. 따라서 `.env` 파일은 필요하지 않습니다. 필요한 데이터베이스 속성은 [Notion DB 구조](docs/notion-schema.md)에 정리되어 있습니다.

## 공개 저장소 안전 기준

- 실제 `data/archive-index.jsonl`은 개인 Notion 페이지 주소가 포함되므로 Git에서 제외합니다.
- 공개할 때는 `data/archive-index.example.jsonl`만 사용합니다.
- 비밀번호, Notion 인증값 또는 API 키를 파일에 기록하지 않습니다.
- 향후 `.env`를 사용하더라도 실제 파일은 Git에 포함되지 않습니다.

## 현재 한계

- 자료 탐색과 저장은 아직 자동 예약 실행이 아닙니다.
- Notion에서 직접 수정한 내용과 로컬 인덱스는 자동 동기화되지 않습니다.
- 실제 자료의 요약과 직무 연결은 사용자가 최종 검토해야 합니다.
