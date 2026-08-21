# Mini Agent 확장 프로젝트 Master Plan

## 1. 프로젝트 목표

현재 구현된 **Agent 1 여행 조회 Agent**는 수정하지 않고 유지한다.

기존 구조와 `Agent Runtime` 실행 흐름을 참고해 다음 두 Agent를 추가한다.

| 구분 | 담당 문서 | Agent | 핵심 역할 |
|---|---|---|---|
| Agent 1 | 기존 구현 | 여행 조회 Agent | 날씨·숙소·관광지 조회 |
| Agent 2 | `dev1.md` | 도서관 도우미 Agent | 도서 검색·대출 가능 여부·장르 추천 |
| Agent 3 | `dev2.md` | 택배 조회 Agent | 배송 상태·예상 도착일·무인 택배함 조회 |

MVP에서는 외부 데이터베이스나 실제 외부 API를 연결하지 않는다. 각 Tool은 재현 가능한 Mock 데이터를 반환하고, 사용자는 Streamlit 화면에서 Agent의 실행 결과를 확인한다.

---

## 2. 공통 Agent 실행 흐름

새 Agent 2개는 기존 `backend/app/agents/runtime.py`의 흐름을 재사용한다.

```text
사용자 질문 입력
→ LLM이 Agent에게 허용된 Tool 중 하나를 선택
→ 필수 arguments 확인
→ Python Backend가 Tool 실행
→ LLM이 Tool Result만 사용해 최종 한국어 답변 작성
→ Frontend가 선택·실행·최종 답변 Trace 표시
```

현재 Runtime은 한 Cycle에서 Tool을 최대 하나만 실행한다. 이번 개발에서 멀티 Tool 반복 호출이나 Agent 간 자동 호출은 구현하지 않는다.

---

## 3. Agent 2: 도서관 도우미

### 기능

1. 키워드로 도서를 검색한다.
2. 도서 ID로 대출 가능 여부를 확인한다.
3. 장르에 맞는 도서를 추천한다.

### Tool

| Tool 이름 | 필수 입력 | 출력 |
|---|---|---|
| `search_books` | `keyword` | 도서 ID, 제목, 작가, 장르 |
| `check_book_availability` | `book_id` | 대출 가능 여부, 반납 예정일 |
| `recommend_books` | `genre` | 장르에 맞는 추천 도서 목록 |

### 예시 질문

```text
파이썬 입문서를 찾아줘
도서 ID 101번을 지금 빌릴 수 있어?
추리소설을 추천해줘
```

### 제외 기능

- 실제 대출·반납·예약
- 회원 로그인
- 실제 도서관 DB 또는 외부 도서 API
- 도서 데이터 등록·수정·삭제

---

## 4. Agent 3: 택배 조회

### 기능

1. 운송장 번호로 현재 배송 상태를 조회한다.
2. 출발지와 도착지를 이용해 예상 도착일을 계산한다.
3. 입력한 지역의 무인 택배함을 조회한다.

### Tool

| Tool 이름 | 필수 입력 | 출력 |
|---|---|---|
| `track_package` | `tracking_number` | 배송 단계, 현재 위치, 갱신 시각 |
| `estimate_delivery` | `origin`, `destination` | 예상 소요일, 예상 도착일 |
| `find_parcel_locker` | `location` | 보관함 이름, 주소, 이용 가능 여부 |

### 예시 질문

```text
운송장 번호 123456 배송 상태를 알려줘
서울에서 부산으로 보내면 언제 도착해?
강남역 근처 무인 택배함을 찾아줘
```

### 제외 기능

- 실제 택배사 API 연결
- 실제 배송 접수·취소·주소 변경
- 실시간 위치 추적
- 결제 또는 개인정보 저장

---

## 5. API 계획

### Agent 2

```text
GET  /api/agents/library/tools
POST /api/agents/library/select
POST /api/agents/library/run
POST /api/agents/library/complete
```

### Agent 3

```text
GET  /api/agents/parcel/tools
POST /api/agents/parcel/select
POST /api/agents/parcel/run
POST /api/agents/parcel/complete
```

`select`는 Tool 선택만 확인하고, `run`은 지정한 Tool을 직접 실행하며, `complete`는 선택 → 실행 → 최종 답변의 전체 Cycle을 실행한다.

---

## 6. 역할 분담

### dev1 담당

- 도서관 도우미 Agent의 Backend 전체 구현
- 도서관 도우미 Frontend 화면과 Client 구현
- 도서관 Agent 테스트 작성
- 두 팀원의 기능이 완성된 뒤 공통 파일 최종 통합

### dev2 담당

- 택배 조회 Agent의 Backend 전체 구현
- 택배 조회 Frontend 화면과 Client 구현
- 택배 Agent 테스트 작성
- 공통 파일을 직접 수정하지 않고 통합에 필요한 이름과 경로를 dev1에게 전달

### 공통 파일 최종 통합 담당

동시 수정에 의한 충돌을 피하기 위해 다음 파일은 **dev1이 마지막에 한 번만 수정**한다.

```text
backend/app/tools/executor.py
backend/app/main.py
frontend/app.py
```

dev2는 위 파일을 수정하지 않는다. dev1은 dev2의 신규 파일이 병합된 것을 확인한 후 Agent 2와 Agent 3을 함께 등록한다.

---

## 7. 수정 허용 범위

### 새로 생성하는 파일

- Agent 2·3의 Agent, Tool, Schema, Router, Test 파일
- Agent 2·3의 Frontend Page와 Client 파일
- 이 프로젝트 계획에 명시된 Markdown 문서

### 필요한 최소 수정만 허용하는 공통 파일

- `backend/app/tools/executor.py`: 신규 Agent Registry에서 Tool을 찾도록 추가
- `backend/app/main.py`: 신규 Router와 Swagger Tag 등록
- `frontend/app.py`: 신규 페이지 두 개를 Navigation에 등록

기존 코드의 삭제·이동·이름 변경은 하지 않는다.

---

## 8. 건드리면 안 되는 사항

다음 기존 Agent 1 관련 파일과 기능은 수정하지 않는다.

```text
backend/app/agents/travel_agent.py
backend/app/agents/runtime.py
backend/app/tools/registry.py
backend/app/tools/travel/
backend/app/tools/weather/
backend/app/routers/stage_03_router.py
backend/app/schemas/stage_03.py
frontend/app_pages/12_tool_schema.py
frontend/app_pages/13_tool_select.py
frontend/app_pages/14_tool_validation.py
frontend/app_pages/15_tool_run.py
frontend/app_pages/16_tool_errors.py
frontend/app_pages/17_agent_cycle.py
frontend/clients/agent_client.py
```

추가 금지 사항은 다음과 같다.

- 기존 API URL 변경 또는 삭제
- 기존 Agent 1 Tool을 신규 Tool로 교체
- `runtime.py` 실행 흐름 변경
- `.env` 및 API Key 수정·공유
- 필요하지 않은 라이브러리 추가
- Backend·Frontend 폴더 재구성
- 기존 테스트를 삭제하거나 통과 조건을 완화
- 담당하지 않은 팀원의 신규 파일 수정

---

## 9. 개발 순서

1. 각 팀원이 담당 Schema와 Mock Tool을 구현한다.
2. 각 팀원이 Agent 파일에서 자기 Tool 목록만 제공한다.
3. 각 팀원이 전용 Router와 테스트를 구현한다.
4. 각 팀원이 전용 Frontend Client와 Page를 구현한다.
5. dev2가 신규 파일 경로와 Registry 상수 이름을 dev1에게 전달한다.
6. dev1이 공통 파일 3개에 두 Agent를 함께 연결한다.
7. 기존 테스트와 신규 테스트를 모두 실행한다.
8. Backend API와 Streamlit 화면에서 Agent 1·2·3을 각각 확인한다.

---

## 10. 전체 완료 기준

- Agent 1의 기존 기능과 테스트가 그대로 동작한다.
- 각 Agent는 자기에게 허용된 Tool만 LLM에게 제공한다.
- 잘못된 Tool 이름은 `TOOL_NOT_ALLOWED`로 거부한다.
- 필수 입력값이 없으면 추측하지 않고 추가 질문을 반환한다.
- 잘못된 arguments는 Pydantic 검증 오류로 처리한다.
- Tool Result에 없는 정보는 최종 답변에서 만들지 않는다.
- 도서관 화면과 택배 화면에서 전체 Agent Cycle을 확인할 수 있다.
- 외부 API 없이 Mock 모드로 재현 가능하게 실행된다.
- 기존 파일을 삭제하거나 폴더 구조를 변경하지 않는다.

