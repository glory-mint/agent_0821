"""도서관 Agent가 사용하는 Tool arguments를 정의합니다."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BookSearchArgs(BaseModel):
    """제목 또는 작가 검색어입니다."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    keyword: str = Field(min_length=1)


class BookAvailabilityArgs(BaseModel):
    """대출 가능 여부를 확인할 도서 ID입니다."""

    model_config = ConfigDict(extra="forbid")
    book_id: int = Field(ge=1)


class BookRecommendationArgs(BaseModel):
    """추천받을 도서 장르입니다."""

    model_config = ConfigDict(extra="forbid")
    genre: Literal["programming", "novel", "mystery", "history", "essay"]

