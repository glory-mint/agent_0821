"""교육용 운송장 번호의 배송 상태를 조회합니다."""

from app.schemas.parcel import PackageTrackingArgs


_MOCK_PACKAGES = {
    "123456": {
        "status": "배송 중",
        "current_location": "대전 허브",
        "updated_at": "2026-08-21T14:30:00+09:00",
    },
    "000111222333": {
        "status": "배송 완료",
        "current_location": "서울 강남구 배송지",
        "updated_at": "2026-08-20T16:10:00+09:00",
    },
    "987654": {
        "status": "집화 완료",
        "current_location": "부산 집화점",
        "updated_at": "2026-08-21T09:15:00+09:00",
    },
}


def track_package(args: PackageTrackingArgs) -> dict:
    """Mock 운송장 번호에 해당하는 현재 배송 상태를 반환합니다."""

    package = _MOCK_PACKAGES.get(args.tracking_number)
    if package is None:
        return {
            "found": False,
            "tracking_number": args.tracking_number,
            "message": "해당 운송장 번호의 Mock 배송 정보를 찾을 수 없습니다.",
            "source": "mock",
        }

    return {
        "found": True,
        "tracking_number": args.tracking_number,
        **package,
        "source": "mock",
    }
