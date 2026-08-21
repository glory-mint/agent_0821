# Backend 전체 구조 및 개발 계획

## 1. 목표

기존 FastAPI 구조와 Agent 1을 유지하면서 도서관 도우미 Agent와 택배 조회 Agent를 독립된 모듈로 추가한다.

```text
Router → Agent → 공통 Runtime → 안전한 Tool 실행 → 최종 답변
```

Agent 역할과 Tool 목록은 Agent별로 분리하고, 공통 Runtime은 기존 파일을 그대로 재사용한다.

---

## 2. 계획된 Backend 구조

```text
backend/
├─ app/
│  ├─ agents/
│  │  ├─ __init__.py
│  │  ├─ runtime.py                    # 기존, 수정 금지
│  │  ├─ travel_agent.py               # 기존 Agent 1, 수정 금지
│  │  ├─ library_agent.py              # 신규 Agent 2
│  │  └─ parcel_agent.py               # 신규 Agent 3
│  │
│  ├─ tools/
│  │  ├─ __init__.py
│  │  ├─ registry.py                   # 기존 여행 Registry, 수정 금지
│  │  ├─ executor.py                   # dev1이 마지막에 신규 Registry 연결
│  │  ├─ travel/                       # 기존, 수정 금지
│  │  ├─ weather/                      # 기존, 수정 금지
│  │  ├─ library/
│  │  │  ├─ __init__.py
│  │  │  ├─ search.py
│  │  │  ├─ availability.py
│  │  │  ├─ recommendation.py
│  │  │  └─ registry.py
│  │  └─ parcel/
│  │     ├─ __init__.py
│  │     ├─ tracking.py
│  │     ├─ delivery.py
│  │     ├─ locker.py
│  │     └─ registry.py
│  │
│  ├─ schemas/
│  │  ├─ stage_03.py                   # 기존, 수정 금지
│  │  ├─ library.py                    # 신규 Agent 2 입력 모델
│  │  └─ parcel.py                     # 신규 Agent 3 입력 모델
│  │
│  ├─ routers/
│  │  ├─ stage_03_router.py            # 기존 Agent 1, 수정 금지
│  │  ├─ library_agent_router.py       # 신규 Agent 2 API
│  │  └─ parcel_agent_router.py        # 신규 Agent 3 API
│  │
│  └─ main.py                          # dev1이 마지막에 Router 등록
│
└─ tests/
   ├─ test_api.py                      # 기존, 수정 금지
   ├─ test_library_agent.py            # 신규 Agent 2 테스트
   └─ test_parcel_agent.py             # 신규 Agent 3 테스트
```

---

## 3. Agent별 Registry 분리 원칙

기존 `app.tools.registry.TOOL_REGISTRY`는 Agent 1의 여행 Tool만 유지한다. 신규 Tool을 이 Dictionary에 직접 추가하지 않는다.

신규 Agent는 각각 별도의 Registry를 가진다.

```python
# app/tools/library/registry.py
LIBRARY_TOOL_REGISTRY = {
    "search_books": ...,
    "check_book_availability": ...,
    "recommend_books": ...,
}
```

```python
# app/tools/parcel/registry.py
PARCEL_TOOL_REGISTRY = {
    "track_package": ...,
    "estimate_delivery": ...,
    "find_parcel_locker": ...,
}
```

이렇게 분리하면 기존 `travel_agent.py`가 신규 Tool을 전달받지 않으므로 Agent 1의 동작을 변경하지 않을 수 있다.

`ToolSpec` 클래스는 기존 `app.tools.registry`에서 import해 재사용한다. 동일한 역할의 클래스를 새로 만들지 않는다.

---

## 4. Agent 2 Backend 계획

### Schema

`backend/app/schemas/library.py`

```text
BookSearchArgs
└─ keyword: str, 빈 문자열 금지

BookAvailabilityArgs
└─ book_id: int, 1 이상

BookRecommendationArgs
└─ genre: programming | novel | mystery | history | essay
```

Pydantic 모델은 `extra="forbid"`를 사용해 정의하지 않은 입력값을 거부한다.

### Tool

```text
search_books(args)
→ keyword가 제목 또는 작가에 포함된 Mock 도서 목록

check_book_availability(args)
→ book_id에 해당하는 대출 가능 여부와 반납 예정일

recommend_books(args)
→ genre와 일치하는 Mock 추천 도서 목록
```

검색 결과가 없거나 존재하지 않는 ID인 경우 정상적인 빈 결과 또는 명확한 Tool Result를 반환한다. 존재하지 않는 데이터를 임의로 생성하지 않는다.

### Agent

`library_agent.py`에는 다음만 둔다.

- Agent 이름
- Tool 선택 지침
- 최종 답변 지침
- `get_library_tools()`
- `select_library_tool()`
- `run_library_agent()`

Agent는 `LIBRARY_TOOL_REGISTRY`의 Tool만 전달한다.

### Router

```text
GET  /api/agents/library/tools
POST /api/agents/library/select
POST /api/agents/library/run
POST /api/agents/library/complete
```

`run` Endpoint는 요청된 Tool 이름이 `LIBRARY_TOOL_REGISTRY`에 있는지 먼저 확인한다. 다른 Agent의 Tool 실행 요청은 `TOOL_NOT_ALLOWED`로 거부한다.

---

## 5. Agent 3 Backend 계획

### Schema

`backend/app/schemas/parcel.py`

```text
PackageTrackingArgs
└─ tracking_number: str, 빈 문자열 금지

DeliveryEstimateArgs
├─ origin: str, 빈 문자열 금지
└─ destination: str, 빈 문자열 금지

ParcelLockerArgs
└─ location: str, 빈 문자열 금지
```

Pydantic 모델은 `extra="forbid"`를 사용한다. 운송장 번호는 예시 형식만 검증하며 실제 개인정보를 저장하지 않는다.

### Tool

```text
track_package(args)
→ Mock 운송장 번호에 해당하는 배송 단계와 현재 위치

estimate_delivery(args)
→ 출발지·도착지 기준의 교육용 예상 소요일과 도착일

find_parcel_locker(args)
→ 입력 지역과 일치하는 Mock 무인 택배함 목록
```

예상 도착일은 실제 택배사의 약속이 아니라 Mock 계산 결과임을 `source: "mock"`과 안내 문구로 표시한다.

### Agent

`parcel_agent.py`에는 다음만 둔다.

- Agent 이름
- Tool 선택 지침
- 최종 답변 지침
- `get_parcel_tools()`
- `select_parcel_tool()`
- `run_parcel_agent()`

Agent는 `PARCEL_TOOL_REGISTRY`의 Tool만 전달한다.

### Router

```text
GET  /api/agents/parcel/tools
POST /api/agents/parcel/select
POST /api/agents/parcel/run
POST /api/agents/parcel/complete
```

`run` Endpoint는 `PARCEL_TOOL_REGISTRY`에 등록된 Tool만 허용한다.

---

## 6. 공통 Executor 통합 계획

`backend/app/tools/executor.py`는 dev1이 최종 통합 단계에서만 수정한다.

조회 순서는 다음과 같이 유지한다.

```text
기존 TOOL_REGISTRY에서 검색
→ 없으면 LIBRARY_TOOL_REGISTRY에서 검색
→ 없으면 PARCEL_TOOL_REGISTRY에서 검색
→ 모두 없으면 TOOL_NOT_ALLOWED
```

기존 `execute_tool_safely(name, arguments)` 함수 이름·인자·반환 모델은 변경하지 않는다. 기존 Validation 오류와 실행 오류 코드도 유지한다.

---

## 7. main.py 통합 계획

dev1이 다음 Router를 추가로 import하고 등록한다.

```python
app.include_router(library_agent_router)
app.include_router(parcel_agent_router)
```

Swagger Tag도 다음 두 개만 추가한다.

```text
04 · 도서관 Agent
05 · 택배 Agent
```

기존 Router 등록 순서와 기존 Tag 내용은 변경하지 않는다.

---

## 8. 테스트 계획

각 Agent 테스트는 최소한 다음을 확인한다.

1. Registry에 담당 Tool 세 개만 등록됐는가?
2. 각 Tool의 정상 arguments가 실행되는가?
3. 필수 arguments 누락을 거부하는가?
4. 정의되지 않은 추가 arguments를 거부하는가?
5. 다른 Agent Tool을 전용 `run` Endpoint에서 거부하는가?
6. Mock Tool Result에 `source: "mock"`이 포함되는가?
7. LLM 호출은 monkeypatch하여 실제 API Key 없이 Cycle을 검사할 수 있는가?
8. 기존 `backend/tests/test_api.py`가 계속 통과하는가?

Mock 테스트 성공과 실제 OpenAI Agent Cycle 성공은 구분해서 기록한다.

---

## 9. Backend 수정 금지 범위

```text
backend/app/agents/runtime.py
backend/app/agents/travel_agent.py
backend/app/tools/registry.py
backend/app/tools/travel/
backend/app/tools/weather/
backend/app/routers/stage_01_router.py
backend/app/routers/stage_02_router.py
backend/app/routers/stage_03_router.py
backend/app/schemas/stage_01.py
backend/app/schemas/stage_02.py
backend/app/schemas/stage_03.py
backend/app/providers/
backend/app/core/config.py
```

다음 작업도 하지 않는다.

- 기존 API 삭제·이름 변경
- 실제 DB 테이블 생성
- 실제 대출·배송 상태 변경 기능
- `.env` 또는 Secret 수정
- 불필요한 의존성 설치
- 기존 테스트 삭제

