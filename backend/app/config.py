"""애플리케이션 설정 로드.

환경변수(컨테이너에서는 docker-compose 가 주입)에서 값을 읽는다.
필드명은 대소문자 무시 매칭이라 DATABASE_URL -> database_url 로 들어온다.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # postgresql+asyncpg://user:pass@db:5432/dbname
    database_url: str
    # HA 가 X-API-Key 헤더로 보낼 Phase 1 공유 키
    api_key: str
    log_level: str = "INFO"

    # --- 활동 상태 분류 임계값 (실데이터로 튜닝 필요) ---
    # 최근 이 시간(초) 안의 readings 로 현재 상태를 판단
    activity_window_seconds: int = 60
    # 평균 movement_score 가 이 값 이상이면 'active'(이동 중)
    activity_active_threshold: float = 0.5
    # 평균 movement_score 가 이 값 이하면 'still'(정지/휴식)
    activity_still_threshold: float = 0.2
    # 윈도 내 (max-min) 변동이 이 값 이상이면 전환 이벤트(앉음/일어섬 등)로 표시
    activity_spike_delta: float = 0.4

    model_config = SettingsConfigDict(
        env_file=".env",      # 로컬 실행 시 참고 (컨테이너엔 없어도 무방)
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
