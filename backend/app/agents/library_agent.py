"""도서관 Agent의 역할·지침·Tool을 정의합니다."""

from typing import Any

from app.agents.runtime import ToolDecision, run_agent, select_tool
from app.schemas.stage_03 import ToolCompleteResult
from app.tools.library.registry import get_library_tool_definitions


LIBRARY_AGENT_NAME = "library_helper_agent"

LIBRARY_AGENT_INSTRUCTIONS = """
당신은 도서관 도우미 Agent입니다.
도서 검색, 대출 가능 여부 확인 또는 장르 추천 질문을 처리하세요.
사용자의 질문을 해결하기 위해 필요한 경우 허용된 도서관 Tool 하나만 선택하세요.
필수 입력값을 추측하지 말고, 도서관 Agent에게 허용된 Tool 외에는 선택하지 마세요.
실제 대출, 반납 또는 예약을 실행했다고 답하지 마세요.
""".strip()

LIBRARY_FINAL_ANSWER_INSTRUCTIONS = """
당신은 친절한 도서관 도우미입니다.
Tool Result에 포함된 정보만 사용해 한국어로 답변하고, 결과에 없는 값은 추측하지 마세요.
Mock 조회 결과를 실제 대출이나 예약이 완료된 것처럼 표현하지 마세요.
""".strip()


def get_library_tools() -> list[dict[str, Any]]:
    """도서관 Agent가 사용할 수 있는 Tool 목록입니다."""
    return get_library_tool_definitions()


def select_library_tool(
    message: str,
    tool_choice: str = "auto",
) -> ToolDecision:
    """도서관 지침과 Tool 목록으로 실행할 Tool을 선택합니다."""
    return select_tool(
        message=message,
        instructions=LIBRARY_AGENT_INSTRUCTIONS,
        tools=get_library_tools(),
        tool_choice=tool_choice,
    )


def run_library_agent(
    message: str,
    tool_choice: str = "auto",
) -> ToolCompleteResult:
    """도서 질문을 Tool 선택 → 실행 → 최종 답변 순서로 처리합니다."""
    return run_agent(
        message=message,
        instructions=LIBRARY_AGENT_INSTRUCTIONS,
        final_answer_instructions=LIBRARY_FINAL_ANSWER_INSTRUCTIONS,
        tools=get_library_tools(),
        tool_choice=tool_choice,
    )

