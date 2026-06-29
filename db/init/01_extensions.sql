-- DB 컨테이너 최초 기동 시 1회 실행됨 (/docker-entrypoint-initdb.d).
-- TimescaleDB: 시계열 하이퍼테이블/압축/보존정책 기능
CREATE EXTENSION IF NOT EXISTS timescaledb;
-- pgcrypto: gen_random_uuid() 사용 (UUID 기본키)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
