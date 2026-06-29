"""readings 관련 입출력 Pydantic 스키마."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReadingCreate(BaseModel):
    """POST /api/v1/readings 요청 본문 (HA 가 보냄)."""
    device_key: str
    # 생략 시 서버 시각 사용
    timestamp: datetime | None = None
    movement_score: float | None = None
    motion_detected: bool
    raw_payload: dict | None = None


class ReadingCreateResponse(BaseModel):
    status: str = "ok"
    stored_at: datetime


class ReadingOut(BaseModel):
    """GET /api/v1/readings 의 개별 항목."""
    time: datetime
    movement_score: float | None
    motion_detected: bool


class ReadingsResponse(BaseModel):
    device_id: UUID
    count: int
    readings: list[ReadingOut]


class AggregatedBucket(BaseModel):
    time: datetime
    avg_movement_score: float | None
    max_movement_score: float | None
    motion_count: int
    no_motion_count: int


class AggregatedResponse(BaseModel):
    device_id: UUID
    bucket: str
    data: list[AggregatedBucket]
