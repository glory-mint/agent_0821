"""입력 지역과 일치하는 교육용 무인 택배함을 검색합니다."""

from app.schemas.parcel import ParcelLockerArgs


_MOCK_LOCKERS = (
    {
        "keywords": ("강남", "강남역", "서울 강남"),
        "name": "강남역 2번 출구 무인 택배함",
        "address": "서울특별시 강남구 강남대로 396",
        "available": True,
    },
    {
        "keywords": ("강남", "역삼", "서울 강남"),
        "name": "역삼 주민센터 무인 택배함",
        "address": "서울특별시 강남구 역삼로 7길 16",
        "available": False,
    },
    {
        "keywords": ("부산역", "부산 동구", "초량"),
        "name": "부산역 광장 무인 택배함",
        "address": "부산광역시 동구 중앙대로 206",
        "available": True,
    },
)


def find_parcel_locker(args: ParcelLockerArgs) -> dict:
    """지역 키워드가 일치하는 Mock 보관함 목록을 반환합니다."""

    query = args.location.casefold()
    items = [
        {key: value for key, value in locker.items() if key != "keywords"}
        for locker in _MOCK_LOCKERS
        if any(query in keyword.casefold() or keyword.casefold() in query for keyword in locker["keywords"])
    ]
    return {"location": args.location, "items": items, "source": "mock"}
