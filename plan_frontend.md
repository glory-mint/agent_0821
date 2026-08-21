# Frontend 전체 구조 및 개발 계획

## 1. 목표

현재 Streamlit 화면 구조를 유지하고, Agent 2와 Agent 3의 전체 Cycle을 확인할 수 있는 페이지를 각각 하나씩 추가한다.

MVP 화면에서는 다음 세 단계가 보이면 된다.

```text
1. LLM이 선택한 Tool과 arguments
2. Python Backend가 반환한 Tool Result
3. Tool Result를 이용한 최종 답변
```

---

## 2. 계획된 Frontend 구조

```text
frontend/
├─ app.py                              # dev1이 마지막에 페이지 2개 등록
│
├─ core/
│  └─ api_client.py                    # 기존 공통 요청, 수정 금지
│
├─ clients/
│  ├─ agent_client.py                  # 기존 Agent 1, 수정 금지
│  ├─ library_client.py                # 신규 Agent 2 Client
│  └─ parcel_client.py                 # 신규 Agent 3 Client
│
└─ app_pages/
   ├─ 01_home.py ~ 17_agent_cycle.py   # 기존 화면, 수정 금지
   ├─ 18_library_agent.py              # 신규 Agent 2 화면
   └─ 19_parcel_agent.py               # 신규 Agent 3 화면
```

---

## 3. 공통 화면 원칙

- 기존 `st.Page`, `st.navigation`, `st.page_link` 방식을 유지한다.
- 기존 `core.api_client.request()`를 재사용한다.
- 페이지에서 `httpx` 또는 `requests`를 직접 호출하지 않는다.
- Backend 오류는 기존 `BackendAPIError`로 처리하고 `st.error()`로 표시한다.
- 응답 Key를 임의로 바꾸지 않고 Backend 응답 계약을 그대로 사용한다.
- Tool Result가 없거나 추가 질문이 필요한 경우 별도 안내를 표시한다.
- 실제 기능처럼 오해하지 않도록 Mock 데이터임을 화면에 표시한다.

---

## 4. Agent 2 도서관 화면 계획

### Client

`frontend/clients/library_client.py`

필요한 함수:

```python
get_library_tools()
select_library_tool(message, tool_choice="auto")
run_library_tool(tool_name, arguments)
complete_library_agent(message, tool_choice="auto")
```

각 함수는 다음 API만 호출한다.

```text
/api/agents/library/tools
/api/agents/library/select
/api/agents/library/run
/api/agents/library/complete
```

### Page

`frontend/app_pages/18_library_agent.py`

화면 구성:

```text
제목: 📚 도서관 도우미 Agent
설명: 도서 검색·대출 가능 여부·장르 추천 Tool 중 하나를 사용합니다.
Tool Choice: auto / none / required
질문 입력: text_input 또는 예시 질문 selectbox
실행 버튼
1. Tool 선택 결과
2. Tool 실행 결과 또는 추가 질문
3. 최종 답변
전체 Trace expander
```

예시 질문:

```text
파이썬 입문서를 찾아줘
도서 ID 101번을 지금 빌릴 수 있어?
추리소설을 추천해줘
```

---

## 5. Agent 3 택배 화면 계획

### Client

`frontend/clients/parcel_client.py`

필요한 함수:

```python
get_parcel_tools()
select_parcel_tool(message, tool_choice="auto")
run_parcel_tool(tool_name, arguments)
complete_parcel_agent(message, tool_choice="auto")
```

각 함수는 다음 API만 호출한다.

```text
/api/agents/parcel/tools
/api/agents/parcel/select
/api/agents/parcel/run
/api/agents/parcel/complete
```

### Page

`frontend/app_pages/19_parcel_agent.py`

화면 구성:

```text
제목: 📦 택배 조회 Agent
설명: 배송 상태·예상 도착일·무인 택배함 Tool 중 하나를 사용합니다.
Tool Choice: auto / none / required
질문 입력: text_input 또는 예시 질문 selectbox
실행 버튼
1. Tool 선택 결과
2. Tool 실행 결과 또는 추가 질문
3. 최종 답변
전체 Trace expander
```

예시 질문:

```text
운송장 번호 123456 배송 상태를 알려줘
서울에서 부산으로 보내면 언제 도착해?
강남역 근처 무인 택배함을 찾아줘
```

---

## 6. app.py 통합 계획

`frontend/app.py`는 dev1이 두 팀원의 페이지가 완성된 후 한 번만 수정한다.

추가할 Page 객체:

```python
library_agent = st.Page(
    "app_pages/18_library_agent.py",
    title="도서관 도우미 Agent",
)

parcel_agent = st.Page(
    "app_pages/19_parcel_agent.py",
    title="택배 조회 Agent",
)
```

두 객체를 기존 `st.navigation()` 목록에 추가하고 Sidebar에 다음 그룹을 추가한다.

```text
04. 추가 Agent
├─ 4-1. 도서관 도우미
└─ 4-2. 택배 조회
```

기존 Page 객체, 기존 Navigation 순서, 기존 Sidebar 그룹은 삭제하거나 이름을 변경하지 않는다.

---

## 7. Frontend 확인 계획

각 페이지에서 다음을 확인한다.

1. 페이지가 Sidebar에서 열리는가?
2. 버튼을 누르기 전 불필요한 API 요청이 발생하지 않는가?
3. 정상 응답의 `decision`, `tool_result`, `final_answer`, `trace`가 보이는가?
4. 필수값 누락 시 `follow_up_question`이 보이는가?
5. Backend 연결 오류가 빈 화면이 아니라 오류 메시지로 보이는가?
6. 기존 Agent 1 페이지가 그대로 열리고 실행되는가?

---

## 8. Frontend 수정 금지 범위

```text
frontend/core/api_client.py
frontend/clients/agent_client.py
frontend/app_pages/01_home.py ~ 17_agent_cycle.py
```

추가 금지 사항:

- 기존 화면 삭제·이름 변경
- 기존 API URL 변경
- CSS 또는 전체 Layout 개편
- Page에서 Backend 로직 재구현
- Mock 결과를 Frontend에 하드코딩
- `.env` 또는 API Key를 화면에 출력
- 담당하지 않은 팀원의 Page·Client 수정

