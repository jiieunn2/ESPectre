"""헬스체크 엔드포인트."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    """서비스와 DB 연결 상태를 반환한다.

    DB 에 `SELECT 1` 을 날려 실제 연결을 확인한다.
    """
    try:
        await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status}
