from fastapi.testclient import TestClient

from app.agents import runtime
from app.agents.library_agent import get_library_tools, select_library_tool
from app.main import app
from app.schemas.library import (
    BookAvailabilityArgs,
    BookRecommendationArgs,
    BookSearchArgs,
)
from app.tools.library import (
    check_book_availability,
    recommend_books,
    search_books,
)
from app.tools.library.registry import LIBRARY_TOOL_REGISTRY


client = TestClient(app)


def test_library_registry_contains_only_library_tools() -> None:
    expected_names = {
        "search_books",
        "check_book_availability",
        "recommend_books",
    }

    assert set(LIBRARY_TOOL_REGISTRY) == expected_names
    assert {tool["name"] for tool in get_library_tools()} == expected_names

    response = client.get("/api/agents/library/tools")
    assert response.status_code == 200
    assert {tool["name"] for tool in response.json()["tools"]} == expected_names


def test_search_books_returns_matches_and_empty_result() -> None:
    result = search_books(BookSearchArgs(keyword="파이썬"))
    assert result["source"] == "mock"
    assert result["count"] == 1
    assert result["items"][0]["book_id"] == 101

    empty_result = search_books(BookSearchArgs(keyword="없는책"))
    assert empty_result["items"] == []
    assert empty_result["count"] == 0


def test_book_availability_handles_available_borrowed_and_unknown() -> None:
    available = check_book_availability(BookAvailabilityArgs(book_id=101))
    assert available["found"] is True
    assert available["available"] is True
    assert "due_date" not in available

    borrowed = check_book_availability(BookAvailabilityArgs(book_id=102))
    assert borrowed["found"] is True
    assert borrowed["available"] is False
    assert borrowed["due_date"]

    unknown = check_book_availability(BookAvailabilityArgs(book_id=999))
    assert unknown["found"] is False
    assert unknown["book_id"] == 999


def test_recommend_books_returns_only_requested_genre() -> None:
    result = recommend_books(BookRecommendationArgs(genre="mystery"))

    assert result["source"] == "mock"
    assert result["items"]
    assert all(book["genre"] == "mystery" for book in result["items"])


def test_library_run_validates_arguments() -> None:
    missing = client.post(
        "/api/agents/library/run",
        json={"tool_name": "search_books", "arguments": {}},
    )
    assert missing.status_code == 200
    assert missing.json()["error"]["code"] == "TOOL_VALIDATION_ERROR"

    extra = client.post(
        "/api/agents/library/run",
        json={
            "tool_name": "search_books",
            "arguments": {"keyword": "파이썬", "unknown": True},
        },
    )
    assert extra.status_code == 200
    assert extra.json()["error"]["code"] == "TOOL_VALIDATION_ERROR"


def test_library_run_blocks_other_agent_tools() -> None:
    response = client.post(
        "/api/agents/library/run",
        json={"tool_name": "get_current_weather", "arguments": {"city": "부산"}},
    )

    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "TOOL_NOT_ALLOWED"


def test_library_tool_can_run_through_common_executor() -> None:
    response = client.post(
        "/api/agents/library/run",
        json={"tool_name": "search_books", "arguments": {"keyword": "FastAPI"}},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["items"][0]["book_id"] == 102


def test_library_tool_selection_uses_only_library_definitions(monkeypatch) -> None:
    class FunctionCall:
        type = "function_call"
        name = "search_books"
        arguments = '{"keyword":"파이썬"}'

    class Responses:
        def __init__(self) -> None:
            self.kwargs = None

        def create(self, **kwargs):
            self.kwargs = kwargs
            return type("Response", (), {"output": [FunctionCall()]})()

    responses = Responses()
    client_double = type("OpenAIClient", (), {"responses": responses})()
    monkeypatch.setattr(runtime, "_openai_client", lambda: client_double)

    decision = select_library_tool("파이썬 책을 찾아줘")

    assert decision.tool_name == "search_books"
    assert decision.arguments == {"keyword": "파이썬"}
    assert {tool["name"] for tool in responses.kwargs["tools"]} == set(
        LIBRARY_TOOL_REGISTRY
    )


def test_library_complete_with_tool_choice_none_needs_no_api_key() -> None:
    response = client.post(
        "/api/agents/library/complete",
        json={"message": "안녕하세요", "tool_choice": "none"},
    )

    assert response.status_code == 200
    assert response.json()["decision"]["tool_name"] is None
    assert response.json()["tool_result"] is None

