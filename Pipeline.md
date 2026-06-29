# ESP32 CSI → Home Assistant → TimescaleDB 데이터 파이프라인 (Phase 1)

ESP32 CSI 센서값(`movement_score`, `motion_detected`)을 Home Assistant 경유로
FastAPI 백엔드에 보내 PostgreSQL + TimescaleDB 에 시계열 저장하는 파이프라인.

## 빠른 시작

```bash
# 1. 환경변수 준비 (이미 .env 가 있으면 생략)
cp .env.example .env   # 그리고 값 채우기

# 2. DB 만 먼저 기동 (Day 1-2)
docker compose up -d db

# 3. DB 접속 확인
docker compose exec db psql -U monitoring -d monitoring -c "\dx"
```

## 구성

```
ESP32-S3 ──WiFi──▶ Home Assistant ──REST POST──▶ FastAPI ──asyncpg──▶ PostgreSQL+TimescaleDB
```

## 디렉토리

- `docker-compose.yml` — 전체 스택 정의
- `db/init/` — DB 최초 기동 시 실행되는 SQL (확장 설치)
- `backend/` — FastAPI 애플리케이션 (Day 3-5 부터)

