"""택배 Agent가 사용할 수 있는 Tool만 별도 Registry로 관리합니다."""

from app.schemas.parcel import DeliveryEstimateArgs, PackageTrackingArgs, ParcelLockerArgs
from app.tools.parcel import estimate_delivery, find_parcel_locker, track_package
from app.tools.registry import ToolSpec


PARCEL_TOOL_REGISTRY: dict[str, ToolSpec] = {
    "track_package": ToolSpec(
        name="track_package",
        description="운송장 번호로 현재 배송 단계와 위치를 조회합니다. 출발지와 도착지만 있는 예상 도착일 질문에는 사용하지 않습니다.",
        input_model=PackageTrackingArgs,
        function=track_package,
    ),
    "estimate_delivery": ToolSpec(
        name="estimate_delivery",
        description="출발지와 도착지로 교육용 예상 배송 소요일과 도착일을 계산합니다. 운송장 번호의 현재 상태 조회에는 사용하지 않습니다.",
        input_model=DeliveryEstimateArgs,
        function=estimate_delivery,
    ),
    "find_parcel_locker": ToolSpec(
        name="find_parcel_locker",
        description="입력한 지역 근처의 교육용 Mock 무인 택배함과 이용 가능 여부를 조회합니다.",
        input_model=ParcelLockerArgs,
        function=find_parcel_locker,
    ),
}


def get_parcel_tool_definitions() -> list[dict]:
    return [tool.definition() for tool in PARCEL_TOOL_REGISTRY.values()]
