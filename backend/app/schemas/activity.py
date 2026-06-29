"""활동 상태 분류 출력 스키마."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ActivityState(BaseModel):
    device_id: UUID
    # active(이동 중) / still(정지) / uncertain(임계값 사이) / no_data
    state: str
    # 윈도 내 movement 변동이 커서 자세 전환(앉음/일어섬)으로 의심되는지
    transition_detected: bool
    window_seconds: int
    samples: int
    mean_movement_score: float | None
    max_movement_score: float | None
    min_movement_score: float | None
    any_motion: bool
    latest_time: datetime | None
    # 판단에 쓰인 임계값 (튜닝 투명성용)
    thresholds: dict
