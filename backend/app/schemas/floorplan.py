"""평면도 입출력 스키마."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FloorPlanCreate(BaseModel):
    """평면도 저장 요청. data 는 자유 구조(JSON)."""
    name: str = Field(default="우리집")
    # 예: {"source":"roomplan","unit":"m","rooms":[{"name":"거실",
    #      "device_key":"esp32-livingroom-01","polygon":[[0,0],[4.2,0],[4.2,3.1],[0,3.1]]}]}
    data: dict


class FloorPlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    data: dict
    created_at: datetime
    updated_at: datetime
