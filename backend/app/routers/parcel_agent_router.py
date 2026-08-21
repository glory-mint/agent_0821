"""택배 Agent의 Tool 목록·선택·실행·전체 Cycle API를 제공합니다."""

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from app.agents.parcel_agent import run_parcel_agent, select_parcel_tool
from app.schemas.stage_03 import (
    ToolCompleteRequest,
    ToolCompleteResult,
    ToolRunRequest,
    ToolRunResult,
    ToolSelectRequest,
    ToolSelectionResult,
)
from app.tools.executor import execute_tool_safely
from app.tools.parcel.registry import PARCEL_TOOL_REGISTRY, get_parcel_tool_definitions


parcel_agent_router = APIRouter(tags=["05 · 택배 Agent"])


@parcel_agent_router.get("/api/agents/parcel/tools")
def parcel_tools() -> dict:
    """Agent를 실행하지 않고 택배 Agent의 허용 Tool만 반환합니다."""

    return {
        "tools": get_parcel_tool_definitions(),
        "note": "모든 결과는 교육용 Mock 데이터이며 택배 전용 Allowlist를 통해 실행됩니다.",
    }


@parcel_agent_router.post("/api/agents/parcel/select", response_model=ToolSelectionResult)
def choose_parcel_tool(payload: ToolSelectRequest) -> ToolSelectionResult:
    """LLM이 택배 Tool과 arguments만 선택하며 Tool은 실행하지 않습니다."""

    try:
        decision = select_parcel_tool(payload.message, payload.tool_choice)
        return ToolSelectionResult.model_validate(asdict(decision))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"OpenAI 택배 Tool 선택에 실패했습니다: {error}") from error


@parcel_agent_router.post("/api/agents/parcel/run", response_model=ToolRunResult)
def execute_parcel_tool(payload: ToolRunRequest) -> ToolRunResult:
    """택배 Agent에 허용된 Tool인지 확인한 뒤 공통 Executor로 실행합니다."""

    if payload.tool_name not in PARCEL_TOOL_REGISTRY:
        return ToolRunResult(
            success=False,
            tool_name=payload.tool_name,
            error={"code": "TOOL_NOT_ALLOWED", "message": "택배 Agent에 허용되지 않은 Tool입니다."},
        )
    return execute_tool_safely(payload.tool_name, payload.arguments)


@parcel_agent_router.post("/api/agents/parcel/complete", response_model=ToolCompleteResult)
def complete_parcel_cycle(payload: ToolCompleteRequest) -> ToolCompleteResult:
    """택배 Tool 선택·실행·최종 답변의 전체 Agent Cycle을 수행합니다."""

    try:
        return run_parcel_agent(payload.message, payload.tool_choice)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"OpenAI 택배 Agent Cycle에 실패했습니다: {error}") from error
