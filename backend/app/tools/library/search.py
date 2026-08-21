"""제목 또는 작가로 교육용 Mock 도서를 검색합니다."""

from typing import TypedDict

from app.schemas.library import BookSearchArgs


class MockBook(TypedDict):
    book_id: int
    title: str
    author: str
    genre: str
    available: bool


MOCK_BOOKS: tuple[MockBook, ...] = (
    {
        "book_id": 101,
        "title": "파이썬 첫걸음",
        "author": "김파이",
        "genre": "programming",
        "available": True,
    },
    {
        "book_id": 102,
        "title": "쉽게 배우는 FastAPI",
        "author": "이개발",
        "genre": "programming",
        "available": False,
    },
    {
        "book_id": 103,
        "title": "마지막 열차의 비밀",
        "author": "박추리",
        "genre": "mystery",
        "available": True,
    },
    {
        "book_id": 104,
        "title": "작은 별의 이야기",
        "author": "최소설",
        "genre": "novel",
        "available": False,
    },
    {
        "book_id": 105,
        "title": "조선의 하루",
        "author": "정역사",
        "genre": "history",
        "available": True,
    },
    {
        "book_id": 106,
        "title": "천천히 걷는 마음",
        "author": "한수필",
        "genre": "essay",
        "available": True,
    },
)


def public_book(book: MockBook) -> dict:
    """대출 상태를 제외한 공개 도서 정보를 반환합니다."""
    return {
        "book_id": book["book_id"],
        "title": book["title"],
        "author": book["author"],
        "genre": book["genre"],
    }


def search_books(args: BookSearchArgs) -> dict:
    """검색어가 제목 또는 작가에 포함된 도서를 반환합니다."""
    keyword = args.keyword.casefold()
    items = [
        public_book(book)
        for book in MOCK_BOOKS
        if keyword in book["title"].casefold() or keyword in book["author"].casefold()
    ]
    return {
        "query": args.keyword,
        "items": items,
        "count": len(items),
        "source": "mock",
    }

