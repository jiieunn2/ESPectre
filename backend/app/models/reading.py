"""시계열 센서 측정값 모델 (TimescaleDB 하이퍼테이블).

PK 는 (time, device_id) — 파티션 컬럼 time 을 반드시 포함해야 하이퍼테이블 변환이 가능하다.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Reading(Base):
    __tablename__ = "readings"

    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, nullable=False
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id"),
        primary_key=True,
        nullable=False,
    )
    movement_score: Mapped[float | None] = mapped_column(Float)
    motion_detected: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # 디버깅용 원본 HA payload
    raw_payload: Mapped[dict | None] = mapped_column(JSONB)
