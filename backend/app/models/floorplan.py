"""집 평면도(2D) 모델.

RoomPlan(또는 다른 소스)으로 스캔/측정한 평면도 geometry 를 JSONB 로 저장한다.
구조를 유연하게 두어(JSONB) 방 폴리곤·치수·센서 배치 등을 자유롭게 담는다.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class FloorPlan(Base):
    __tablename__ = "floor_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    # geometry: 예) {"source":"roomplan","unit":"m",
    #   "rooms":[{"name":"거실","device_key":"esp32-livingroom-01",
    #             "polygon":[[0,0],[4.2,0],[4.2,3.1],[0,3.1]]}]}
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
