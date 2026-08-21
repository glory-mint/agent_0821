"""교육용 Mock 도서의 대출 가능 여부를 확인합니다."""

from datetime import date, timedelta

from app.schemas.library import BookAvailabilityArgs
from app.tools.library.search import MOCK_BOOKS, public_book


def check_book_availability(args: BookAvailabilityArgs) -> dict:
    """도서 ID가 존재하면 대출 상태를 반환합니다."""
    book = next((item for item in MOCK_BOOKS if item["book_id"] == args.book_id), None)
    if book is None:
        return {
            "found": False,
            "book_id": args.book_id,
            "message": "해당 도서를 찾을 수 없습니다.",
            "source": "mock",
        }

    result = {
        "found": True,
        "book": public_book(book),
        "available": book["available"],
        "source": "mock",
    }
    if not book["available"]:
        result["due_date"] = (date.today() + timedelta(days=7)).isoformat()
    return result

