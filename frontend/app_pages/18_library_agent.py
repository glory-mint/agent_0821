import streamlit as st

from clients.library_client import complete_library_agent
from core.api_client import BackendAPIError


st.title("📚 도서관 도우미 Agent")
st.caption("도서 검색·대출 가능 여부·장르 추천 Tool 중 하나를 사용합니다.")
st.info("도서 정보와 대출 상태는 학습을 위한 Mock 데이터입니다.")

tool_choice = st.selectbox("Tool Choice", ["auto", "none", "required"])
example_question = st.selectbox(
    "예시 질문",
    [
        "파이썬 입문서를 찾아줘",
        "도서 ID 101번을 지금 빌릴 수 있어?",
        "추리소설을 추천해줘",
    ],
)
custom_question = st.text_input(
    "직접 질문",
    placeholder="비워두면 위의 예시 질문을 사용합니다.",
)
message = custom_question.strip() or example_question

st.code(
    "질문 → ① LLM이 도서관 Tool 선택 → ② Python이 Mock Tool 실행 → ③ LLM이 최종 답변",
    language="text",
)

if st.button("도서관 Agent 실행", type="primary"):
    try:
        result = complete_library_agent(message, tool_choice)
        decision = result["decision"]

        st.subheader("1. LLM이 Tool과 arguments 선택")
        st.json(decision)

        st.subheader("2. Python Backend가 Tool 실행")
        if decision["needs_clarification"]:
            st.warning(decision["follow_up_question"])
        elif result["tool_result"] is None:
            st.info("실행할 도서관 Tool이 없습니다.")
        else:
            st.json(result["tool_result"])

        st.subheader("3. LLM이 사용자용 최종 답변 생성")
        st.success(result["final_answer"])

        with st.expander("전체 Cycle Trace", expanded=True):
            st.json(result["trace"])
    except BackendAPIError as error:
        st.error(str(error))

