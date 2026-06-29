"""장치 목록 라우터 (/api/v1/devices)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..dependencies import verify_api_key
from ..models import Device
from ..schemas.device import DeviceOut

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("", response_model=list[DeviceOut])
async def list_devices(
    session: AsyncSession = Depends(get_session),
) -> list[Device]:
    """등록된 모든 장치 목록."""
    res = await session.execute(select(Device).order_by(Device.created_at))
    return list(res.scalars().all())
