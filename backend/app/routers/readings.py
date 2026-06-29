"""센서 데이터 적재/조회 라우터 (/api/v1/readings)."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..dependencies import verify_api_key
from ..schemas.reading import (
    AggregatedBucket,
    AggregatedResponse,
    ReadingCreate,
    ReadingCreateResponse,
    ReadingOut,
    ReadingsResponse,
)
from ..services.ingest import ingest_reading

router = APIRouter(
    prefix="/readings",
    tags=["readings"],
    dependencies=[Depends(verify_api_key)],  # 모든 엔드포인트에 X-API-Key 요구
)

# 허용 버킷 -> timedelta (asyncpg 는 interval 파라미터로 timedelta 를 요구)
_BUCKET_MAP = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1),
}


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReadingCreateResponse)
async def create_reading(
    payload: ReadingCreate,
    session: AsyncSession = Depends(get_session),
) -> ReadingCreateResponse:
    """HA 가 센서값 1건을 적재한다."""
    stored_at = await ingest_reading(session, payload)
    return ReadingCreateResponse(status="ok", stored_at=stored_at)


@router.get("", response_model=ReadingsResponse)
async def get_readings(
    device_id: UUID,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(1000, ge=1, le=10000),
    session: AsyncSession = Depends(get_session),
) -> ReadingsResponse:
    """원시 측정값 조회. 기본 범위: 최근 24시간."""
    now = datetime.now(timezone.utc)
    start = start or (now - timedelta(hours=24))
    end = end or now

    q = text(
        """
        SELECT time, movement_score, motion_detected
        FROM readings
        WHERE device_id = :device_id AND time >= :start AND time <= :end
        ORDER BY time DESC
        LIMIT :limit
        """
    )
    res = await session.execute(
        q,
        {"device_id": str(device_id), "start": start, "end": end, "limit": limit},
    )
    rows = res.mappings().all()
    readings = [
        ReadingOut(
            time=r["time"],
            movement_score=r["movement_score"],
            motion_detected=r["motion_detected"],
        )
        for r in rows
    ]
    return ReadingsResponse(device_id=device_id, count=len(readings), readings=readings)


@router.get("/aggregated", response_model=AggregatedResponse)
async def get_aggregated(
    device_id: UUID,
    bucket: str = Query("1h"),
    start: datetime | None = None,
    end: datetime | None = None,
    session: AsyncSession = Depends(get_session),
) -> AggregatedResponse:
    """TimescaleDB time_bucket 기반 시간 버킷 집계."""
    if bucket not in _BUCKET_MAP:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"invalid bucket '{bucket}', allowed: {list(_BUCKET_MAP)}",
        )
    interval = _BUCKET_MAP[bucket]
    now = datetime.now(timezone.utc)
    start = start or (now - timedelta(hours=24))
    end = end or now

    q = text(
        """
        SELECT
            time_bucket(:interval, time) AS bucket_time,
            AVG(movement_score) AS avg_movement_score,
            MAX(movement_score) AS max_movement_score,
            SUM(CASE WHEN motion_detected THEN 1 ELSE 0 END) AS motion_count,
            SUM(CASE WHEN NOT motion_detected THEN 1 ELSE 0 END) AS no_motion_count
        FROM readings
        WHERE device_id = :device_id AND time >= :start AND time <= :end
        GROUP BY bucket_time
        ORDER BY bucket_time
        """
    )
    res = await session.execute(
        q,
        {"interval": interval, "device_id": str(device_id), "start": start, "end": end},
    )
    rows = res.mappings().all()
    data = [
        AggregatedBucket(
            time=r["bucket_time"],
            avg_movement_score=r["avg_movement_score"],
            max_movement_score=r["max_movement_score"],
            motion_count=r["motion_count"],
            no_motion_count=r["no_motion_count"],
        )
        for r in rows
    ]
    return AggregatedResponse(device_id=device_id, bucket=bucket, data=data)
