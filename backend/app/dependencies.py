"""공용 FastAPI 의존성: API Key 검증 등."""
from fastapi import Header, HTTPException, status

from .config import settings


async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """X-API-Key 헤더가 설정된 공유 키와 일치하는지 확인 (Phase 1).

    불일치/누락 시 401.
    """
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing X-API-Key",
        )
