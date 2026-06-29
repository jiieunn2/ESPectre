"""initial schema: devices, readings, users, user_devices

Revision ID: 0001
Revises:
Create Date: 2026-06-12

readings 는 여기서는 일반 테이블로 만든다. 하이퍼테이블 변환은 0002 에서.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- devices ---
    op.execute(
        """
        CREATE TABLE devices (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            device_key VARCHAR(64) UNIQUE NOT NULL,
            name VARCHAR(128) NOT NULL,
            location VARCHAR(128),
            firmware_version VARCHAR(32),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            last_seen_at TIMESTAMPTZ
        );
        """
    )

    # --- readings (일반 테이블, 0002 에서 하이퍼테이블로 변환) ---
    op.execute(
        """
        CREATE TABLE readings (
            time TIMESTAMPTZ NOT NULL,
            device_id UUID NOT NULL REFERENCES devices(id),
            movement_score DOUBLE PRECISION,
            motion_detected BOOLEAN NOT NULL,
            raw_payload JSONB,
            PRIMARY KEY (time, device_id)
        );
        """
    )
    op.execute(
        "CREATE INDEX idx_readings_device_time ON readings (device_id, time DESC);"
    )

    # --- users (Phase 2 대비) ---
    op.execute(
        """
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            role VARCHAR(16) NOT NULL CHECK (role IN ('self', 'guardian')),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
    )

    # --- user_devices (Phase 2 대비) ---
    op.execute(
        """
        CREATE TABLE user_devices (
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            device_id UUID REFERENCES devices(id) ON DELETE CASCADE,
            relationship VARCHAR(16) NOT NULL CHECK (relationship IN ('owner', 'monitor')),
            PRIMARY KEY (user_id, device_id)
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_devices;")
    op.execute("DROP TABLE IF EXISTS users;")
    op.execute("DROP TABLE IF EXISTS readings;")
    op.execute("DROP TABLE IF EXISTS devices;")
