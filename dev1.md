# dev1 역할 분담: 도서관 도우미 Agent

## 1. 담당 목표

도서 검색·대출 가능 여부·장르 추천을 처리하는 **Agent 2 도서관 도우미**를 구현한다.

추가로 두 팀원의 기능 개발이 끝난 뒤 공통 연결 파일 3개를 최종 통합한다.

---

## 2. dev1 전용 생성 파일

```text
backend/app/agents/library_agent.py
backend/app/tools/library/__init__.py
backend/app/tools/library/search.py
backend/app/tools/library/availability.py
backend/app/tools/library/recommendation.py
backend/app/tools/library/registry.py
backend/app/schemas/library.py
backend/app/routers/library_agent_router.py
backend/tests/test_library_agent.py
frontend/clients/library_client.py
frontend/app_pages/18_library_agent.py
```

위 파일은 dev1이 소유한다. dev2의 택배 파일은 수정하지 않는다.

---

## 3. Backend 구현 사항

### 3-1. Schema

`backend/app/schemas/library.py`

```python
BookSearchArgs
- keyword: str
- 최소 길이 1

BookAvailabilityArgs
- book_id: int
- 1 이상

BookRecommendationArgs
- genre: programming | novel | mystery | history | essay
```

모든 모델에 `ConfigDict(extra="forbid")`를 적용한다.

### 3-2. Mock Tool

`search.py`

```python
search_books(args: BookSearchArgs) -> dict
```

- 제목 또는 작가에 `keyword`가 포함된 도서를 반환한다.
- 결과에는 `book_id`, `title`, `author`, `genre`를 포함한다.
- 결과가 없으면 빈 `items`를 반환한다.
- `source`는 항상 `"mock"`으로 표시한다.

`availability.py`

```python
check_book_availability(args: BookAvailabilityArgs) -> dict
```

- 알려진 `book_id`는 대출 가능 여부를 반환한다.
- 대출 중인 책만 `due_date`를 반환한다.
- 존재하지 않는 ID는 존재하지 않음을 명확하게 반환한다.

`recommendation.py`

```python
recommend_books(args: BookRecommendationArgs) -> dict
```

- 입력 장르와 일치하는 도서만 반환한다.
- 결과에 없는 평점·재고·추천 이유를 임의로 만들지 않는다.

### 3-3. 전용 Registry

`backend/app/tools/library/registry.py`

```python
LIBRARY_TOOL_REGISTRY = {
    "search_books": ToolSpec(...),
    "check_book_availability": ToolSpec(...),
    "recommend_books": ToolSpec(...),
}
```

- 기존 `app.tools.registry.ToolSpec`을 재사용한다.
- 기존 `TOOL_REGISTRY`는 수정하지 않는다.
- LLM용 Tool 설명에서 언제 사용하고 언제 사용하지 않는지 구분한다.
- `get_library_tool_definitions()` 함수를 제공한다.

### 3-4. Agent

`backend/app/agents/library_agent.py`

다음 상수와 함수만 구현한다.

```text
LIBRARY_AGENT_NAME
LIBRARY_AGENT_INSTRUCTIONS
LIBRARY_FINAL_ANSWER_INSTRUCTIONS
get_library_tools()
select_library_tool()
run_library_agent()
```

지침에는 다음 규칙을 포함한다.

- 도서 관련 질문만 처리한다.
- 필수값을 추측하지 않는다.
- 도서관 Agent의 Tool 외에는 선택하지 않는다.
- 최종 답변은 Tool Result에 포함된 정보만 사용한다.
- 실제 대출·예약이 완료된 것처럼 답하지 않는다.

### 3-5. Router

`backend/app/routers/library_agent_router.py`

```text
GET  /api/agents/library/tools
POST /api/agents/library/select
POST /api/agents/library/run
POST /api/agents/library/complete
```

- 기존 `stage_03`의 공통 요청·응답 모델은 import해 재사용한다.
- `run` 요청의 Tool 이름이 `LIBRARY_TOOL_REGISTRY`에 없으면 `TOOL_NOT_ALLOWED`를 반환한다.
- OpenAI 설정 누락은 422, 외부 LLM 호출 실패는 502로 구분한다.

---

## 4. Frontend 구현 사항

### 4-1. Client

`frontend/clients/library_client.py`

```python
get_library_tools()
select_library_tool(message, tool_choice="auto")
run_library_tool(tool_name, arguments)
complete_library_agent(message, tool_choice="auto")
```

기존 `core.api_client.request()`를 사용한다.

### 4-2. Page

`frontend/app_pages/18_library_agent.py`

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

## 5. dev1 테스트 사항

`backend/tests/test_library_agent.py`

최소 테스트:

1. Registry에 도서 Tool 세 개만 존재한다.
2. `search_books` 정상 검색과 빈 검색 결과를 확인한다.
3. `check_book_availability`의 대출 가능·대출 중·없는 ID를 확인한다.
4. `recommend_books`가 입력 장르만 반환한다.
5. 필수값 누락과 추가 필드를 거부한다.
6. 도서 Router가 택배·여행 Tool 이름을 거부한다.
7. 실제 OpenAI API를 부르지 않도록 LLM 선택 부분을 monkeypatch한다.

---

## 6. dev1 공통 통합 담당

dev2가 택배 신규 파일 구현과 테스트를 끝낸 후에만 다음 파일을 수정한다.

```text
backend/app/tools/executor.py
backend/app/main.py
frontend/app.py
```

### executor.py

- 기존 `TOOL_REGISTRY` 조회를 그대로 유지한다.
- `LIBRARY_TOOL_REGISTRY`, `PARCEL_TOOL_REGISTRY` 조회를 추가한다.
- 기존 함수 이름·인자·오류 코드는 변경하지 않는다.

### main.py

- `library_agent_router`, `parcel_agent_router`를 import한다.
- 두 Router를 `include_router()`로 등록한다.
- Swagger Tag 두 개를 추가한다.
- 기존 Router와 Tag는 변경하지 않는다.

### frontend/app.py

- `18_library_agent.py`, `19_parcel_agent.py` Page를 등록한다.
- Sidebar에 두 페이지 링크를 추가한다.
- 기존 Page와 Sidebar는 변경하지 않는다.

---

## 7. dev1이 건드리면 안 되는 사항

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
backend/app/agents/parcel_agent.py
backend/app/tools/parcel/
backend/app/schemas/parcel.py
backend/app/routers/parcel_agent_router.py
frontend/clients/parcel_client.py
frontend/app_pages/19_parcel_agent.py
```

추가로 다음을 하지 않는다.

- 실제 대출·예약 구현
- DB 또는 외부 도서 API 연결
- `.env`, API Key, `requirements.txt` 수정
- 기존 코드 삭제·이동·이름 변경
- dev2 코드의 임의 리팩터링

---

## 8. dev1 완료 기준

- 도서 Tool 세 개가 Mock 데이터로 동작한다.
- 도서 Agent가 도서 Tool만 선택한다.
- 도서 API 네 개가 Swagger에 표시된다.
- 도서 Frontend에서 전체 Cycle을 확인할 수 있다.
- 도서 테스트와 기존 테스트가 통과한다.
- 통합 후 택배 Agent도 등록되며 기존 여행 Agent가 그대로 동작한다.

