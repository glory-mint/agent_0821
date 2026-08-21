"""출발지와 도착지에 따른 교육용 예상 도착일을 계산합니다."""

from datetime import date, timedelta

from app.schemas.parcel import DeliveryEstimateArgs


_ROUTE_DAYS = {
    frozenset(("서울", "부산")): 2,
    frozenset(("서울", "대전")): 1,
    frozenset(("서울", "대구")): 2,
    frozenset(("부산", "대전")): 2,
    frozenset(("부산", "대구")): 1,
}


def _estimated_days(origin: str, destination: str) -> int:
    if origin == destination:
        return 1
    if "제주" in origin or "제주" in destination:
        return 3
    return _ROUTE_DAYS.get(frozenset((origin, destination)), 2)


def estimate_delivery(args: DeliveryEstimateArgs) -> dict:
    """고정된 Mock 지역 규칙으로 예상 소요일과 도착일을 반환합니다."""

    estimated_days = _estimated_days(args.origin, args.destination)
    estimated_arrival = date.today() + timedelta(days=estimated_days)
    return {
        "origin": args.origin,
        "destination": args.destination,
        "estimated_days": estimated_days,
        "estimated_arrival": estimated_arrival.isoformat(),
        "notice": "교육용 Mock 계산 결과이며 실제 택배사의 배송 시간을 보장하지 않습니다.",
        "source": "mock",
    }
