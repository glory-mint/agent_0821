import streamlit as st

from clients.parcel_client import complete_parcel_agent
from core.api_client import BackendAPIError


st.title("📦 택배 조회 Agent")
st.caption("배송 상태·예상 도착일·무인 택배함 Tool 중 하나를 사용합니다.")
st.info("이 화면의 배송 정보와 예상 도착일은 실제 택배사 정보가 아닌 교육용 Mock 데이터입니다.")

tool_choice = st.selectbox("Tool Choice", ["auto", "none", "required"])
example = st.selectbox(
    "예시 질문",
    [
        "운송장 번호 123456 배송 상태를 알려줘",
        "서울에서 부산으로 보내면 언제 도착해?",
        "강남역 근처 무인 택배함을 찾아줘",
        "직접 입력",
    ],
)
message = st.text_input("직접 질문 입력") if example == "직접 입력" else example

st.code("질문 → ① LLM이 택배 Tool 선택 → ② Python이 실행 → ③ LLM이 최종 답변", language="text")

if st.button("택배 Agent Cycle 실행", type="primary"):
    if not message.strip():
        st.warning("택배 조회 질문을 입력해 주세요.")
    else:
        try:
            result = complete_parcel_agent(message, tool_choice)
            decision = result["decision"]

            st.subheader("1. LLM이 Tool과 arguments 선택")
            st.json(decision)

            st.subheader("2. Python Backend가 Tool 실행")
            if decision["needs_clarification"]:
                st.warning(decision["follow_up_question"])
            elif result["tool_result"] is None:
                st.info("실행할 택배 Tool이 없습니다.")
            else:
                st.json(result["tool_result"])

            st.subheader("3. LLM이 사용자용 최종 답변 생성")
            st.success(result["final_answer"])

            with st.expander("전체 Cycle Trace", expanded=True):
                st.json(result["trace"])
        except BackendAPIError as error:
            st.error(str(error))
