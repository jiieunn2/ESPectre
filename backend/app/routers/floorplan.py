"""평면도 저장/조회 라우터 (/api/v1/floorplans)."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..dependencies import verify_api_key
from ..models import FloorPlan
from ..schemas.floorplan import FloorPlanCreate, FloorPlanOut

router = APIRouter(
    prefix="/floorplans",
    tags=["floorplans"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=FloorPlanOut)
async def create_floorplan(
    payload: FloorPlanCreate,
    session: AsyncSession = Depends(get_session),
) -> FloorPlan:
    """평면도 1건 저장(스캔 결과 업로드)."""
    plan = FloorPlan(name=payload.name, data=payload.data)
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return plan


@router.get("/latest", response_model=FloorPlanOut)
async def latest_floorplan(
    session: AsyncSession = Depends(get_session),
) -> FloorPlan:
    """가장 최근 평면도(앱이 기본으로 띄울 것)."""
    res = await session.execute(
        select(FloorPlan).order_by(FloorPlan.created_at.desc()).limit(1)
    )
    plan = res.scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=404, detail="no floor plan saved yet")
    return plan


@router.get("", response_model=list[FloorPlanOut])
async def list_floorplans(
    session: AsyncSession = Depends(get_session),
) -> list[FloorPlan]:
    """저장된 평면도 목록(최신순)."""
    res = await session.execute(select(FloorPlan).order_by(FloorPlan.created_at.desc()))
    return list(res.scalars().all())


@router.get("/{plan_id}", response_model=FloorPlanOut)
async def get_floorplan(
    plan_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> FloorPlan:
    plan = await session.get(FloorPlan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="floor plan not found")
    return plan
