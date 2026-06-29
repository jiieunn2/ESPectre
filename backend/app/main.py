"""FastAPI 애플리케이션 진입점."""
import logging
from pathlib import Path

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

from .config import settings
from .routers import analysis, devices, floorplan, health, readings

# 구조화 로깅 최소 설정
logging.basicConfig(level=settings.log_level)
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(
        logging.getLevelName(settings.log_level)
    ),
)
log = structlog.get_logger()

app = FastAPI(
    title="ESP32 Monitoring API",
    version="0.1.0",
    description="ESP32 CSI 센서 데이터 적재/조회 API (Phase 1)",
)

# 헬스체크 (prefix 없음)
app.include_router(health.router)
# 비즈니스 API (/api/v1/*)
app.include_router(readings.router, prefix="/api/v1")
app.include_router(devices.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(floorplan.router, prefix="/api/v1")


# ---- 평면도 정적 페이지 (Home Assistant iframe 용) ----
# backend/static/ 에 둔 HTML 을 같은 origin(:8000)으로 서빙 → CORS 불필요.
# 컨테이너 경로 /app/static (호스트: backend/static, docker-compose 의 ./backend:/app 마운트).
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/floorplan", tags=["floorplan-ui"], include_in_schema=False)
async def floorplan_editor() -> FileResponse:
    """평면도 에디터(설정용): 방 그리기 → 센서 연결 → 저장."""
    return FileResponse(STATIC_DIR / "floorplan.html")


@app.get("/floorplan/view", tags=["floorplan-ui"], include_in_schema=False)
async def floorplan_view_page() -> FileResponse:
    """평면도 보기 전용(Location iframe용): 저장된 평면도 + 실시간 상태 색칠."""
    return FileResponse(STATIC_DIR / "floorplan-view.html")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """예상치 못한 예외를 500 으로 변환하고 구조화 로그를 남긴다.

    (HTTPException / 검증 오류는 FastAPI 기본 핸들러가 먼저 처리한다.)
    """
    log.error("unhandled_error", path=str(request.url), error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "internal server error"})


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """루트: 살아있는지 + 문서 위치 안내."""
    return {"service": "esp32-monitoring", "docs": "/docs", "health": "/healthz"}
