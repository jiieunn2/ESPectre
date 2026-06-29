"""POST /api/v1/readings 비즈니스 로직."""
from datetime import datetime, timezone

import structlog
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Device, Reading
from ..schemas.reading import ReadingCreate

log = structlog.get_logger()


async def ingest_reading(session: AsyncSession, payload: ReadingCreate) -> datetime:
    """센서 측정값 1건을 적재하고 stored_at(time) 을 반환한다.

    - device_key 로 장치를 찾고, 없으면 404.
    - timestamp 생략 시 서버 UTC 시각 사용.
    - 같은 (time, device_id) 가 들어오면 덮어쓴다(upsert).
    - 장치의 last_seen_at 갱신.
    """
    result = await session.execute(
        select(Device).where(Device.device_key == payload.device_key)
    )
    device = result.scalar_one_or_none()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"device_key not found: {payload.device_key}",
        )

    ts = payload.timestamp or datetime.now(timezone.utc)

    stmt = (
        pg_insert(Reading)
        .values(
            time=ts,
            device_id=device.id,
            movement_score=payload.movement_score,
            motion_detected=payload.motion_detected,
            raw_payload=payload.raw_payload,
        )
        .on_conflict_do_update(
            index_elements=["time", "device_id"],
            set_={
                "movement_score": payload.movement_score,
                "motion_detected": payload.motion_detected,
                "raw_payload": payload.raw_payload,
            },
        )
    )
    await session.execute(stmt)
    await session.execute(
        update(Device).where(Device.id == device.id).values(last_seen_at=ts)
    )
    await session.commit()

    log.info(
        "reading_ingested",
        device_key=payload.device_key,
        time=ts.isoformat(),
        movement_score=payload.movement_score,
        motion_detected=payload.motion_detected,
    )
    return ts
