# 서브에이전트 수집 흐름과 결과 형식

## 목적

새로 찾는 HR·MD 자료는 조사·검수를 거치고, 직접 링크는 품질 검수 없이 원문을 요약한다. 두 경로는 같은 템플릿·Notion DB·중복 기록을 사용한다. 서브에이전트는 읽기 전용이며 메인 에이전트가 유일한 작성자다. Slack과 웹 라이브러리는 명시적으로 요청했을 때만 사용하는 선택 기능이다.

## 전체 흐름

```text
HR 자료 조사 ─┐
              ├─> 통합 검수 ─> 메인: Notion 저장·재확인·로컬 기록
MD 자료 조사 ─┘
```

사용자 URL은 별도 탐색 없이 다음 흐름을 사용한다.

```text
사용자 URL ─> 중복 확인 ─> 본문 접근·원문 요약 ─> 메인: Notion 저장·재확인·로컬 기록
```

- 입력은 URL 최대 5개와 `summary_only` 여부다.
- `summary_only=true`이면 요약 결과만 보여주고 Notion, 로컬 인덱스·판단·실행 기록, Slack과 라이브러리를 변경하지 않는다. 이는 요청형 수집에도 동일하다.
- 본문 접근에 실패한 URL은 후보 객체를 만들지 않고 `notes`에 URL과 실패 이유만 기록한다.
- 사용자가 추가 탐색을 요청하지 않았다면 입력 URL 외의 자료를 후보로 추가하지 않는다.
- 직접 링크는 A/B/C 등급, 최신성, 자료 유형으로 선별하지 않으며 `result_reviewer`에게 전달하지 않는다. 관련성이 약한 분류·요약 영역은 생략할 수 있지만 그것을 저장 거절 사유로 삼지 않는다.
- 같은 URL은 기존 저장 링크를 안내한다. 재요약만 요청하면 원문을 다시 읽되 기존 페이지를 덮어쓰지 않는다. 서로 다른 직접 링크는 같은 주제라는 이유로 제외하지 않는다.
- 5개를 넘는 링크는 초과분을 알리고 다음 묶음으로 안내한다. 입력 링크와 추가 수집을 함께 요청하면 링크부터 처리한 뒤 탐색 결과만 검수한다.

## 요청형 수집 입력

메인 에이전트는 요청한 직무 담당자에게 `target_role`, `target_count`, 요청 주제·기간과 기존 축적 현황을 전달한다. 건수가 없으면 요청 직무별 2건, 직무도 없으면 HR 2건·MD 2건이 기본 목표다. 목표는 중복 제외·검수 후 저장 건수이며, 부족하면 이유를 알리고 종료한다. 두 직무와 관련된 한 자료는 한 페이지만 저장하고 전체 저장 건수도 1건으로 센다.

## 조사 에이전트 결과

조사 에이전트는 JSON 하나만 반환한다. `candidates`는 전달받은 `target_count` 이하(기본 최대 2건)이며 기준을 통과한 자료가 없으면 빈 배열이다. 이 형식은 새 자료를 탐색하는 HR·MD 조사에만 사용한다.

```json
{
  "agent": "hr_researcher 또는 md_researcher",
  "status": "completed 또는 partial",
  "searched_at": "ISO 8601 시각",
  "candidates": [
    {
      "candidate_id": "직무-날짜-순번",
      "target_role": "HR 또는 MD",
      "purpose": "직무 공부 또는 산업·기업 동향",
      "title": "원문 제목",
      "source": "출처",
      "published_at": "YYYY-MM-DD",
      "material_type": "뉴스, 기업 공식 홈페이지, 기술 블로그, 공식 YouTube, 보고서·공공자료, 기타 중 하나",
      "source_priority": "direct_practitioner, detailed_case, specialist_reporting, general_news 중 하나",
      "source_priority_reason": "이 순위로 판단한 근거와 더 높은 순위 원출처 확인 결과",
      "canonical_url": "원문 URL",
      "work_areas": ["기존 Notion 업무 영역 값"],
      "key_facts": [
        {
          "fact": "원문에서 확인한 핵심 사실",
          "evidence": "해당 사실을 확인한 원문 근거의 짧은 요약"
        }
      ],
      "case_flow": [
        {
          "stage": "problem, role, judgment, action, collaboration, outcome, failure_or_improvement 중 하나",
          "detail": "원문에서 확인한 현업 사례 요소",
          "evidence": "해당 요소를 확인한 원문 근거의 짧은 요약"
        }
      ],
      "role_reflection": {
        "source_basis": "원문에서 확인한 실제 선택 또는 충돌하는 목표",
        "decision_criteria": ["사용자가 비교해볼 직무 판단 기준"],
        "question": "사용자가 담당자 관점에서 판단해볼 질문 1개"
      },
      "selection_reason": "A등급 세 기준을 충족하는 이유",
      "limitations": ["확인 한계가 있을 때만 작성"]
    }
  ],
  "notes": ["자료가 부족하거나 조사가 일부 실패한 경우만 작성"]
}
```

`case_flow`, `role_reflection`, `limitations`와 확인되지 않은 `published_at`은 선택 필드다. 조건을 충족하지 않으면 키 자체를 생략하며 빈 배열, 빈 문자열, `null`, `확인 불가`, `정보 없음` 같은 대체 값을 반환하지 않는다.

- `case_flow`는 서로 연결되는 요소가 2개 이상이고 그중 `judgment` 또는 `action`이 있을 때만 포함한다. 확인되는 단계만 배열에 넣는다.
- `role_reflection`은 원문에 실제 선택 또는 충돌하는 목표가 있고 직무 판단 기준을 근거로 제시할 수 있을 때만 포함한다.
- `limitations`는 출처 신뢰성이나 해석에 영향을 주는 중요한 한계가 있을 때만 포함한다.

## 검수 에이전트 결과

검수 에이전트는 새로 탐색한 후보의 원문과 로컬 인덱스를 대조한 뒤 JSON 하나만 반환한다. 직접 링크에는 적용하지 않는다. 조사 결과의 사실을 새로 쓰지 않고 판정과 문제만 덧붙인다.

```json
{
  "agent": "result_reviewer",
  "status": "completed 또는 partial",
  "decisions": [
    {
      "candidate_id": "조사 결과의 candidate_id",
      "decision": "pass, hold, reject 중 하나",
      "roles": ["HR 또는 MD, 양쪽 직접 관련이면 둘 다"],
      "reason": "판정 근거 한두 문장",
      "duplicate_of": "중복이 아니면 null, 중복이면 대표 candidate_id 또는 기존 URL",
      "failed_checks": ["문제가 있는 검사항목"],
      "removed_optional_fields": ["근거 부족으로 제거한 선택 필드 경로"],
      "verified_candidate": "pass일 때 근거 없는 선택 필드를 제거한 검수 완료 후보 객체"
    }
  ],
  "summary": {
    "pass": 0,
    "hold": 0,
    "reject": 0
  }
}
```

선택 필드만 근거가 부족하면 해당 필드를 제거하고 `removed_optional_fields`에 기록한 뒤 핵심 사실과 A등급 기준이 유효한 후보는 통과시킬 수 있다. 핵심 사실, 출처 또는 A등급 기준에 문제가 있으면 `hold`나 `reject`로 판정한다. 검수 과정에서 새로운 사실이나 해석을 추가하지 않는다.

## 직접 링크 결과

`url_analyzer`는 최대 5개 URL을 처리하고 다음 JSON을 반환한다. 성공한 원문은 `items`, 읽지 못한 원문은 `notes`로 분리한다. 품질 등급, `selection_reason`, `source_priority`, `pass/hold/reject`는 만들지 않는다. `status`는 담당자 간 전달용이며 사용자에게 관리용 처리 상태를 요구하지 않는다.

```json
{
  "agent": "url_analyzer",
  "status": "completed",
  "items": [
    {
      "input_url": "https://example.com/article?utm_source=share",
      "canonical_url": "https://example.com/article",
      "title": "원문 제목",
      "material_type": "기타",
      "key_facts": [
        {"fact": "본문에서 확인한 사실", "evidence": "해당 부분의 짧은 근거 요약"}
      ]
    }
  ]
}
```

확인되는 `source`, `published_at`, `purpose`, `roles`, `work_areas`, `role_connection`, `why_it_matters`만 추가한다. 근거 없는 분류·직무 연결·취업 의미를 만들어 넣지 않는다. 원문의 사실과 해석은 구분한다. `case_flow`, `role_reflection`, `limitations`는 위의 공통 작성 조건을 충족할 때만 추가한다.

실패한 링크는 `notes`에 `input_url`, `reason`, `suggested_action`(예: 본문 붙여넣기)을 담는다. 본문 일부·제목·검색 결과만으로 성공 항목을 만들지 않는다. 사용자가 본문을 붙여주면 제공받은 범위로 정리하고 접근 한계를 구분한다. 선택 필드는 내용이 없으면 생략하되 성공 항목이 하나도 없을 때의 `items: []`는 정상이다.

## 선택 기능: 브리핑 작성 입력

Slack 전송을 명시적으로 요청한 경우에만 메인 에이전트가 Notion 저장과 페이지 재확인에 성공한 자료를 다음 형식으로 전달한다.

```json
{
  "run_date": "YYYY-MM-DD",
  "mode": "direct_url 또는 requested_collection",
  "archived_records": [
    {
      "candidate_id": "후보 ID",
      "title": "제목",
      "roles": ["HR 또는 MD"],
      "key_facts": ["원문에서 확인한 핵심 사실"],
      "why_it_matters": "근거가 있는 취업 준비 의미",
      "canonical_url": "원문 URL",
      "notion_page_url": "저장을 확인한 Notion 페이지 URL"
    }
  ]
}
```

직접 링크에 근거 있는 `roles`, `why_it_matters`가 없으면 해당 키를 생략한다. 0건이면 `notes`에 실제 이유를 전달한다. 브리핑 작성 에이전트는 Slack 메시지 본문만 반환한다. 실제 전송은 메인 에이전트가 수행한다.

## 실패 처리

- 조사 한쪽 실패: 성공한 직무의 결과는 계속 검수하고 실패 직무를 실행 기록에 남긴다.
- 검수 실패: 해당 탐색 결과의 Notion 저장과 Slack 전송을 중단한다. 품질 검수를 사용하지 않는 직접 링크 경로에는 적용하지 않는다.
- 선택 필드 일부만 근거 부족: 해당 필드를 제거하고 제거 내역을 기록한 뒤 핵심 기준이 유효하면 계속 진행한다.
- `hold`: 외부 저장 없이 사용자 확인이 필요한 이유를 보고한다.
- Notion 저장 실패: 해당 자료를 영구 인덱스와 Slack PICK에서 제외한다.
- Notion 생성·읽기 확인 불확실: 반환된 페이지 ID·URL을 실행 기록에 남겨 해당 페이지를 확인하고, 확인 전에는 새 페이지를 반복 생성하지 않는다.
- Slack 실패: Notion과 영구 인덱스 결과는 유지하고 오류만 기록한다.
- Slack 전송 여부 불확실: 자동 재전송하지 않고 채널 확인이 필요하다고 기록한다.
- 자료 0건: Notion에 새 페이지를 만들지 않고 실제 이유를 대화에 알린다. Slack 전송은 별도로 요청했을 때만 수행한다.

## 완료 보고

- 직접 링크: 입력 수, 저장 수, 중복·접근 실패·저장 실패와 미처리 링크를 짧게 알리고, 저장 또는 기존 자료의 제목·Notion 링크를 제공한다. 품질 탈락 수는 만들지 않는다.
- 요청형 수집: 요청 직무별 목표·저장·부족 건수와 이유, 저장된 제목·Notion 링크를 제공한다.
- 두 모드 모두 Notion 저장 확인 전에는 완료라고 말하지 않는다. `요약만`이면 저장하지 않았음을 명시한다.
