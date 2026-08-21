"""도서관 Agent의 Tool 조회·선택·실행·전체 Cycle API입니다."""

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from app.agents.library_agent import run_library_agent, select_library_tool
from app.schemas.stage_03 import (
    ToolCompleteRequest,
    ToolCompleteResult,
    ToolRunRequest,
    ToolRunResult,
    ToolSelectRequest,
    ToolSelectionResult,
)
from app.tools.executor import execute_tool_safely
from app.tools.library.registry import (
    LIBRARY_TOOL_REGISTRY,
    get_library_tool_definitions,
)


library_agent_router = APIRouter(tags=["04 · 도서관 Agent"])


@library_agent_router.get("/api/agents/library/tools")
def library_tools() -> dict:
    """Agent를 실행하지 않고 도서관 Tool 명세만 반환합니다."""
    return {
        "tools": get_library_tool_definitions(),
        "note": "도서관 Tool은 교육용 Mock 데이터를 조회합니다.",
    }


@library_agent_router.post(
    "/api/agents/library/select",
    response_model=ToolSelectionResult,
)
def choose_library_tool(payload: ToolSelectRequest) -> ToolSelectionResult:
    """LLM이 도서관 Tool과 arguments만 선택하며 Tool은 실행하지 않습니다."""
    try:
        decision = select_library_tool(payload.message, payload.tool_choice)
        return ToolSelectionResult.model_validate(asdict(decision))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI 도서관 Tool 선택에 실패했습니다: {error}",
        ) from error


@library_agent_router.post(
    "/api/agents/library/run",
    response_model=ToolRunResult,
)
def execute_library_tool(payload: ToolRunRequest) -> ToolRunResult:
    """도서관 Agent에게 허용된 Tool만 직접 실행합니다."""
    if payload.tool_name not in LIBRARY_TOOL_REGISTRY:
        return ToolRunResult(
            success=False,
            tool_name=payload.tool_name,
            error={
                "code": "TOOL_NOT_ALLOWED",
                "message": "도서관 Agent에 허용되지 않은 Tool입니다.",
            },
        )
    return execute_tool_safely(payload.tool_name, payload.arguments)


@library_agent_router.post(
    "/api/agents/library/complete",
    response_model=ToolCompleteResult,
)
def complete_library_agent(payload: ToolCompleteRequest) -> ToolCompleteResult:
    """도서관 Tool 선택·실행·최종 답변의 전체 Cycle을 수행합니다."""
    try:
        return run_library_agent(payload.message, payload.tool_choice)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI 도서관 Agent Cycle에 실패했습니다: {error}",
        ) from error

