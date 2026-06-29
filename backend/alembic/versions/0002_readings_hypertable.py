"""readings 를 TimescaleDB 하이퍼테이블로 변환 + 압축/보존 정책

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-12
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # readings 를 하이퍼테이블로 변환 (테이블이 비어 있어 migrate_data 불필요)
    op.execute("SELECT create_hypertable('readings', 'time');")

    # 압축 설정: device_id 기준으로 세그먼트
    op.execute(
        """
        ALTER TABLE readings SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'device_id'
        );
        """
    )

    # 7일 지난 청크 자동 압축
    op.execute("SELECT add_compression_policy('readings', INTERVAL '7 days');")

    # 90일 지난 데이터 자동 삭제 (Phase 1 기본값)
    op.execute("SELECT add_retention_policy('readings', INTERVAL '90 days');")


def downgrade() -> None:
    op.execute("SELECT remove_retention_policy('readings', if_exists => true);")
    op.execute("SELECT remove_compression_policy('readings', if_exists => true);")
    op.execute("ALTER TABLE readings SET (timescaledb.compress = false);")
    # 하이퍼테이블 자체는 일반 테이블로 되돌리지 않음(0001 downgrade 에서 DROP).
