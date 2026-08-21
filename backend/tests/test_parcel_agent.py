from datetime import date, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.agents import runtime
from app.agents.parcel_agent import get_parcel_tools, select_parcel_tool
from app.routers import parcel_agent_router as parcel_router_module
from app.schemas.parcel import DeliveryEstimateArgs, PackageTrackingArgs, ParcelLockerArgs
from app.schemas.stage_03 import ToolRunResult
from app.tools.parcel import estimate_delivery, find_parcel_locker, track_package
from app.tools.parcel.registry import PARCEL_TOOL_REGISTRY
from app.tools.registry import ToolSpec


api_app = FastAPI()
api_app.include_router(parcel_router_module.parcel_agent_router)
client = TestClient(api_app)


def test_registry_contains_only_three_parcel_tools() -> None:
    assert set(PARCEL_TOOL_REGISTRY) == {
        "track_package",
        "estimate_delivery",
        "find_parcel_locker",
    }
    assert {tool["name"] for tool in get_parcel_tools()} == set(PARCEL_TOOL_REGISTRY)
    assert all(isinstance(tool, ToolSpec) for tool in PARCEL_TOOL_REGISTRY.values())


def test_track_package_returns_known_and_unknown_results() -> None:
    known = track_package(PackageTrackingArgs(tracking_number="123456"))
    unknown = track_package(PackageTrackingArgs(tracking_number="not-registered"))

    assert known == {
        "found": True,
        "tracking_number": "123456",
        "status": "배송 중",
        "current_location": "대전 허브",
        "updated_at": "2026-08-21T14:30:00+09:00",
        "source": "mock",
    }
    assert unknown["found"] is False
    assert unknown["tracking_number"] == "not-registered"
    assert unknown["source"] == "mock"


def test_estimate_delivery_uses_mock_route_rule() -> None:
    result = estimate_delivery(DeliveryEstimateArgs(origin="서울", destination="부산"))

    assert result["estimated_days"] == 2
    assert result["estimated_arrival"] == (date.today() + timedelta(days=2)).isoformat()
    assert "보장하지 않습니다" in result["notice"]
    assert result["source"] == "mock"


def test_find_parcel_locker_returns_matches_and_empty_items() -> None:
    matched = find_parcel_locker(ParcelLockerArgs(location="강남역"))
    empty = find_parcel_locker(ParcelLockerArgs(location="검색 결과 없는 지역"))

    assert matched["items"]
    assert all({"name", "address", "available"} <= set(item) for item in matched["items"])
    assert empty["items"] == []
    assert matched["source"] == empty["source"] == "mock"


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("track_package", {}),
        ("estimate_delivery", {"origin": "서울"}),
        ("find_parcel_locker", {"location": "강남", "unknown": True}),
        ("track_package", {"tracking_number": "   "}),
    ],
)
def test_parcel_tool_schemas_reject_missing_extra_and_blank_values(tool_name: str, arguments: dict) -> None:
    with pytest.raises(ValidationError):
        PARCEL_TOOL_REGISTRY[tool_name].execute(arguments)


def test_parcel_router_exposes_four_api_contracts() -> None:
    paths = {route.path for route in parcel_router_module.parcel_agent_router.routes}
    assert paths == {
        "/api/agents/parcel/tools",
        "/api/agents/parcel/select",
        "/api/agents/parcel/run",
        "/api/agents/parcel/complete",
    }

    response = client.get("/api/agents/parcel/tools")
    assert response.status_code == 200
    assert {item["name"] for item in response.json()["tools"]} == set(PARCEL_TOOL_REGISTRY)


@pytest.mark.parametrize("tool_name", ["get_current_weather", "search_books"])
def test_parcel_router_rejects_other_agent_tools(tool_name: str, monkeypatch) -> None:
    monkeypatch.setattr(
        parcel_router_module,
        "execute_tool_safely",
        lambda *_args, **_kwargs: pytest.fail("다른 Agent Tool은 공통 Executor로 전달하면 안 됩니다."),
    )
    response = client.post(
        "/api/agents/parcel/run",
        json={"tool_name": tool_name, "arguments": {}},
    )

    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "TOOL_NOT_ALLOWED"


def test_parcel_router_passes_allowed_tool_to_common_executor(monkeypatch) -> None:
    def fake_executor(name: str, arguments: dict) -> ToolRunResult:
        assert name == "track_package"
        data = PARCEL_TOOL_REGISTRY[name].execute(arguments)
        return ToolRunResult(success=True, tool_name=name, data=data)

    monkeypatch.setattr(parcel_router_module, "execute_tool_safely", fake_executor)
    response = client.post(
        "/api/agents/parcel/run",
        json={"tool_name": "track_package", "arguments": {"tracking_number": "123456"}},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["source"] == "mock"


def test_openai_selection_receives_only_parcel_tools(monkeypatch) -> None:
    class FunctionCall:
        type = "function_call"
        name = "track_package"
        arguments = '{"tracking_number":"123456"}'

    class Responses:
        def __init__(self) -> None:
            self.kwargs = None

        def create(self, **kwargs):
            self.kwargs = kwargs
            return type("Response", (), {"output": [FunctionCall()]})()

    responses = Responses()
    client_double = type("OpenAIClient", (), {"responses": responses})()
    monkeypatch.setattr(runtime, "_openai_client", lambda: client_double)

    decision = select_parcel_tool("운송장 번호 123456 배송 상태를 알려줘")

    assert decision.tool_name == "track_package"
    assert decision.arguments == {"tracking_number": "123456"}
    assert {tool["name"] for tool in responses.kwargs["tools"]} == set(PARCEL_TOOL_REGISTRY)


def test_missing_selected_argument_requests_clarification(monkeypatch) -> None:
    class FunctionCall:
        type = "function_call"
        name = "estimate_delivery"
        arguments = '{"origin":"서울"}'

    response = type("Response", (), {"output": [FunctionCall()]})()
    responses = type("Responses", (), {"create": lambda self, **kwargs: response})()
    client_double = type("OpenAIClient", (), {"responses": responses})()
    monkeypatch.setattr(runtime, "_openai_client", lambda: client_double)

    decision = select_parcel_tool("서울에서 보내면 언제 도착해?")

    assert decision.needs_clarification is True
    assert decision.missing_arguments == ["destination"]
    assert "destination" in decision.follow_up_question
