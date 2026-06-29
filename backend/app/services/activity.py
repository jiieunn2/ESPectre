"""활동 상태 분류 로직.

CSI movement_score 는 '움직임의 양'이므로, 정지한 앉음/서있음을 구분하진 못한다.
여기서는 최근 윈도의 평균 움직임으로 'active(이동) / still(정지)' 를 나누고,
변동 폭(max-min)이 크면 자세 전환 이벤트로 표시한다.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings


def classify_activity(rows: list[dict]) -> dict:
    """최근 readings(dict 리스트)로 활동 상태를 계산한다.

    rows 항목: {"time", "movement_score", "motion_detected"}
    """
    if not rows:
        return {
            "state": "no_data",
            "transition_detected": False,
            "samples": 0,
            "mean_movement_score": None,
            "max_movement_score": None,
            "min_movement_score": None,
            "any_motion": False,
            "latest_time": None,
        }

    scores = [r["movement_score"] for r in rows if r["movement_score"] is not None]
    any_motion = any(bool(r["motion_detected"]) for r in rows)
    latest_time = max(r["time"] for r in rows)

    mean_s = sum(scores) / len(scores) if scores else None
    max_s = max(scores) if scores else None
    min_s = min(scores) if scores else None

    # 상태 판정
    if mean_s is None:
        # 점수가 전부 NULL 이면 motion 플래그로만 판단
        state = "active" if any_motion else "still"
    elif mean_s >= settings.activity_active_threshold or any_motion:
        state = "active"
    elif mean_s <= settings.activity_still_threshold:
        state = "still"
    else:
        state = "uncertain"  # 임계값 사이 (튜닝 필요 구간)

    # 전환 이벤트: 윈도 내 변동 폭이 크면 자세 변화 의심
    transition = (
        max_s is not None
        and min_s is not None
        and (max_s - min_s) >= settings.activity_spike_delta
    )

    return {
        "state": state,
        "transition_detected": transition,
        "samples": len(rows),
        "mean_movement_score": mean_s,
        "max_movement_score": max_s,
        "min_movement_score": min_s,
        "any_motion": any_motion,
        "latest_time": latest_time,
    }


async def get_activity_state(session: AsyncSession, device_id: UUID) -> dict:
    """DB 에서 최근 윈도 readings 를 읽어 활동 상태를 반환한다."""
    window = settings.activity_window_seconds
    since = datetime.now(timezone.utc) - timedelta(seconds=window)

    q = text(
        """
        SELECT time, movement_score, motion_detected
        FROM readings
        WHERE device_id = :device_id AND time >= :since
        ORDER BY time DESC
        """
    )
    res = await session.execute(q, {"device_id": str(device_id), "since": since})
    rows = [dict(r) for r in res.mappings().all()]

    result = classify_activity(rows)
    result["device_id"] = device_id
    result["window_seconds"] = window
    result["thresholds"] = {
        "active_threshold": settings.activity_active_threshold,
        "still_threshold": settings.activity_still_threshold,
        "spike_delta": settings.activity_spike_delta,
    }
    return result
