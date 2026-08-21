# dev2 역할 분담: 택배 조회 Agent

## 1. 담당 목표

배송 상태·예상 도착일·무인 택배함 조회를 처리하는 **Agent 3 택배 조회 Agent**를 구현한다.

공통 파일은 수정하지 않고, 택배 전용 신규 파일을 완성한 뒤 dev1에게 통합 정보를 전달한다.

---

## 2. dev2 전용 생성 파일

```text
backend/app/agents/parcel_agent.py
backend/app/tools/parcel/__init__.py
backend/app/tools/parcel/tracking.py
backend/app/tools/parcel/delivery.py
backend/app/tools/parcel/locker.py
backend/app/tools/parcel/registry.py
backend/app/schemas/parcel.py
backend/app/routers/parcel_agent_router.py
backend/tests/test_parcel_agent.py
frontend/clients/parcel_client.py
frontend/app_pages/19_parcel_agent.py
```

위 파일은 dev2가 소유한다. dev1의 도서관 파일은 수정하지 않는다.

---

## 3. Backend 구현 사항

### 3-1. Schema

`backend/app/schemas/parcel.py`

```python
PackageTrackingArgs
- tracking_number: str
- 최소 길이 1

DeliveryEstimateArgs
- origin: str
- destination: str
- 각 필드 최소 길이 1

ParcelLockerArgs
- location: str
- 최소 길이 1
```

모든 모델에 `ConfigDict(extra="forbid")`를 적용한다.

### 3-2. Mock Tool

`tracking.py`

```python
track_package(args: PackageTrackingArgs) -> dict
```

- 정해진 교육용 운송장 번호의 배송 상태를 반환한다.
- 결과에 `tracking_number`, `status`, `current_location`, `updated_at`을 포함한다.
- 존재하지 않는 번호는 조회 결과가 없음을 명확히 반환한다.
- 실제 개인정보나 실제 운송장 번호를 저장하지 않는다.

`delivery.py`

```python
estimate_delivery(args: DeliveryEstimateArgs) -> dict
```

- Mock 지역 규칙에 따라 예상 소요일과 도착일을 계산한다.
- 결과에 `origin`, `destination`, `estimated_days`, `estimated_arrival`을 포함한다.
- 실제 택배사의 보장 시간이 아니라는 안내를 포함한다.

`locker.py`

```python
find_parcel_locker(args: ParcelLockerArgs) -> dict
```

- 입력 지역과 일치하는 Mock 보관함을 반환한다.
- 결과에 `name`, `address`, `available`을 포함한다.
- 결과가 없으면 빈 `items`를 반환한다.

모든 Tool Result에 `source: "mock"`을 포함한다.

### 3-3. 전용 Registry

`backend/app/tools/parcel/registry.py`

```python
PARCEL_TOOL_REGISTRY = {
    "track_package": ToolSpec(...),
    "estimate_delivery": ToolSpec(...),
    "find_parcel_locker": ToolSpec(...),
}
```

- 기존 `app.tools.registry.ToolSpec`을 재사용한다.
- 기존 `TOOL_REGISTRY`는 수정하지 않는다.
- Tool 설명에 선택 조건을 분명하게 작성한다.
- `get_parcel_tool_definitions()` 함수를 제공한다.

### 3-4. Agent

`backend/app/agents/parcel_agent.py`

다음 상수와 함수만 구현한다.

```text
PARCEL_AGENT_NAME
PARCEL_AGENT_INSTRUCTIONS
PARCEL_FINAL_ANSWER_INSTRUCTIONS
get_parcel_tools()
select_parcel_tool()
run_parcel_agent()
```

지침에는 다음 규칙을 포함한다.

- 택배 조회 관련 질문만 처리한다.
- 운송장 번호·출발지·도착지·지역을 추측하지 않는다.
- 택배 Agent Tool 외에는 선택하지 않는다.
- Tool Result에 포함된 정보만 최종 답변에 사용한다.
- 실제 접수·주소 변경·배송 취소가 가능하다고 답하지 않는다.

### 3-5. Router

`backend/app/routers/parcel_agent_router.py`

```text
GET  /api/agents/parcel/tools
POST /api/agents/parcel/select
POST /api/agents/parcel/run
POST /api/agents/parcel/complete
```

- 기존 `stage_03`의 공통 요청·응답 모델을 import해 재사용한다.
- `run` 요청의 Tool 이름이 `PARCEL_TOOL_REGISTRY`에 없으면 `TOOL_NOT_ALLOWED`를 반환한다.
- OpenAI 설정 누락은 422, 외부 LLM 호출 실패는 502로 구분한다.

---

## 4. Frontend 구현 사항

### 4-1. Client

`frontend/clients/parcel_client.py`

```python
get_parcel_tools()
select_parcel_tool(message, tool_choice="auto")
run_parcel_tool(tool_name, arguments)
complete_parcel_agent(message, tool_choice="auto")
```

기존 `core.api_client.request()`를 사용한다.

### 4-2. Page

`frontend/app_pages/19_parcel_agent.py`

필수 화면 요소:

- 제목과 Mock 데이터 안내
- `auto`, `none`, `required` Tool Choice
- 예시 질문과 직접 입력
- Agent Cycle 실행 버튼
- `decision` 표시
- `tool_result` 또는 `follow_up_question` 표시
- `final_answer` 표시
- 전체 `trace` Expander
- `BackendAPIError` 오류 표시

---

## 5. dev2 테스트 사항

`backend/tests/test_parcel_agent.py`

최소 테스트:

1. Registry에 택배 Tool 세 개만 존재한다.
2. 알려진 운송장과 존재하지 않는 운송장을 확인한다.
3. 출발지·도착지에 따른 예상 소요일 결과를 확인한다.
4. 보관함 검색의 정상 결과와 빈 결과를 확인한다.
5. 필수값 누락과 추가 필드를 거부한다.
6. 택배 Router가 도서·여행 Tool 이름을 거부한다.
7. 실제 OpenAI API를 부르지 않도록 LLM 선택 부분을 monkeypatch한다.

공통 Executor와 `main.py` 연결 전에는 Tool 함수·Registry·Router 단위 테스트를 먼저 수행한다. 전체 API 통합 테스트는 dev1의 공통 파일 연결 후 함께 수행한다.

---

## 6. dev1에게 전달할 통합 정보

구현을 마치면 다음 내용을 dev1에게 전달한다.

```text
Router 객체:
app.routers.parcel_agent_router.parcel_agent_router

Registry 객체:
app.tools.parcel.registry.PARCEL_TOOL_REGISTRY

Frontend Page:
frontend/app_pages/19_parcel_agent.py

Swagger Tag:
05 · 택배 Agent
```

전달 전 신규 파일 목록과 테스트 결과를 함께 확인한다.

---

## 7. dev2가 건드리면 안 되는 사항

### 공통 통합 파일

```text
backend/app/tools/executor.py
backend/app/main.py
frontend/app.py
```

위 세 파일은 dev1이 최종 통합한다.

### 기존 Agent 1 파일

```text
backend/app/agents/runtime.py
backend/app/agents/travel_agent.py
backend/app/tools/registry.py
backend/app/tools/travel/
backend/app/tools/weather/
backend/app/routers/stage_03_router.py
backend/app/schemas/stage_03.py
frontend/clients/agent_client.py
frontend/app_pages/01_home.py ~ 17_agent_cycle.py
```

### dev1 전용 파일

```text
backend/app/agents/library_agent.py
backend/app/tools/library/
backend/app/schemas/library.py
backend/app/routers/library_agent_router.py
backend/tests/test_library_agent.py
frontend/clients/library_client.py
frontend/app_pages/18_library_agent.py
```

추가로 다음을 하지 않는다.

- 실제 배송 접수·취소·주소 변경 구현
- 실제 택배 API 또는 DB 연결
- `.env`, API Key, `requirements.txt` 수정
- 기존 코드 삭제·이동·이름 변경
- dev1 코드의 임의 리팩터링

---

## 8. dev2 완료 기준

- 택배 Tool 세 개가 Mock 데이터로 동작한다.
- 택배 Agent가 택배 Tool만 LLM에게 제공한다.
- 택배 Router가 네 API 계약을 제공한다.
- 택배 Frontend Page와 Client가 완성된다.
- 택배 단위 테스트가 통과한다.
- 공통 통합에 필요한 객체 이름과 파일 경로를 dev1에게 전달한다.

