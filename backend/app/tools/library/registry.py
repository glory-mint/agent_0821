"""도서관 Agent 전용 Tool 명세를 등록합니다."""

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
from app.tools.registry import ToolSpec


LIBRARY_TOOL_REGISTRY: dict[str, ToolSpec] = {
    "search_books": ToolSpec(
        name="search_books",
        description="도서 제목 또는 작가 키워드로 도서를 검색합니다. 도서 ID의 대출 가능 여부 확인에는 사용하지 않습니다.",
        input_model=BookSearchArgs,
        function=search_books,
    ),
    "check_book_availability": ToolSpec(
        name="check_book_availability",
        description="도서 ID로 현재 대출 가능 여부를 확인합니다. 제목 검색이나 장르 추천에는 사용하지 않습니다.",
        input_model=BookAvailabilityArgs,
        function=check_book_availability,
    ),
    "recommend_books": ToolSpec(
        name="recommend_books",
        description="programming, novel, mystery, history, essay 중 지정한 장르에 맞는 도서를 추천합니다. 특정 제목 검색에는 사용하지 않습니다.",
        input_model=BookRecommendationArgs,
        function=recommend_books,
    ),
}


def get_library_tool_definitions() -> list[dict]:
    """LLM에게 전달할 도서관 Tool 정의만 반환합니다."""
    return [tool.definition() for tool in LIBRARY_TOOL_REGISTRY.values()]

