"""택배 조회 Agent의 역할·지침·허용 Tool을 정의합니다."""

from typing import Any

from app.agents.runtime import ToolDecision, run_agent, select_tool
from app.schemas.stage_03 import ToolCompleteResult
from app.tools.parcel.registry import get_parcel_tool_definitions


PARCEL_AGENT_NAME = "parcel_lookup_agent"

PARCEL_AGENT_INSTRUCTIONS = """
당신은 배송 상태, 예상 도착일, 무인 택배함을 조회하는 택배 Agent입니다.
택배 조회 관련 질문만 처리하고, 질문을 해결하는 데 필요한 택배 Tool 하나를 선택하세요.
운송장 번호, 출발지, 도착지 또는 조회 지역이 부족하면 값을 추측하지 마세요.
허용된 택배 Agent Tool 외에는 선택하지 마세요.
실제 배송 접수, 취소 또는 주소 변경이 가능하다고 답하지 마세요.
""".strip()

PARCEL_FINAL_ANSWER_INSTRUCTIONS = """
당신은 친절한 택배 조회 도우미입니다.
Tool Result에 포함된 정보만 사용해 한국어로 답변하고, 결과에 없는 상태나 날짜를 추측하지 마세요.
Mock 안내 문구가 있으면 실제 택배사의 보장 정보가 아니라는 점을 분명히 전달하세요.
실제 배송 접수, 취소 또는 주소 변경을 완료했다고 답하지 마세요.
""".strip()


def get_parcel_tools() -> list[dict[str, Any]]:
    """택배 Agent에게 택배 전용 Tool 명세만 제공합니다."""

    return get_parcel_tool_definitions()


def select_parcel_tool(
    message: str,
    tool_choice: str = "auto",
) -> ToolDecision:
    """택배 Agent 지침으로 실행할 Tool과 arguments를 선택합니다."""

    return select_tool(
        message=message,
        instructions=PARCEL_AGENT_INSTRUCTIONS,
        tools=get_parcel_tools(),
        tool_choice=tool_choice,
    )


def run_parcel_agent(
    message: str,
    tool_choice: str = "auto",
) -> ToolCompleteResult:
    """택배 질문을 Tool 선택, 실행, 최종 답변 순서로 처리합니다."""

    return run_agent(
        message=message,
        instructions=PARCEL_AGENT_INSTRUCTIONS,
        final_answer_instructions=PARCEL_FINAL_ANSWER_INSTRUCTIONS,
        tools=get_parcel_tools(),
        tool_choice=tool_choice,
    )
