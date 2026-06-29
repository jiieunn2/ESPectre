"""활동 상태 분석 라우터 (/api/v1/devices/{device_id}/state)."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..dependencies import verify_api_key
from ..schemas.activity import ActivityState
from ..services.activity import get_activity_state

router = APIRouter(
    prefix="/devices",
    tags=["analysis"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/{device_id}/state", response_model=ActivityState)
async def device_state(
    device_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ActivityState:
    """장치의 현재 활동 상태(active/still/uncertain) + 최근 통계."""
    data = await get_activity_state(session, device_id)
    return ActivityState(**data)
