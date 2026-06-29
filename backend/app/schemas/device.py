"""devices 관련 출력 스키마."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_key: str
    name: str
    location: str | None
    last_seen_at: datetime | None
