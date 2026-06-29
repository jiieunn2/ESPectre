"""비동기 SQLAlchemy 엔진 / 세션 설정."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import settings

# asyncpg 기반 비동기 엔진
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,  # 끊긴 커넥션 자동 감지
)

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 의존성: 요청마다 DB 세션을 주입하고 끝나면 닫는다."""
    async with AsyncSessionLocal() as session:
        yield session
