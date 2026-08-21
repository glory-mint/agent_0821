"""택배 Agent Tool의 입력값을 검증하는 Pydantic 모델입니다."""

from pydantic import BaseModel, ConfigDict, Field


class ParcelArgsModel(BaseModel):
    """택배 Tool이 공통으로 사용하는 엄격한 입력 검증 설정입니다."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PackageTrackingArgs(ParcelArgsModel):
    tracking_number: str = Field(min_length=1)


class DeliveryEstimateArgs(ParcelArgsModel):
    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)


class ParcelLockerArgs(ParcelArgsModel):
    location: str = Field(min_length=1)
