"""선택한 장르의 교육용 Mock 도서를 추천합니다."""

from app.schemas.library import BookRecommendationArgs
from app.tools.library.search import MOCK_BOOKS, public_book


def recommend_books(args: BookRecommendationArgs) -> dict:
    """입력 장르와 일치하는 도서만 반환합니다."""
    items = [
        public_book(book)
        for book in MOCK_BOOKS
        if book["genre"] == args.genre
    ]
    return {
        "genre": args.genre,
        "items": items,
        "count": len(items),
        "source": "mock",
    }

