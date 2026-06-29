"""모든 ORM 모델의 공통 베이스."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base. metadata 에 모든 테이블이 등록된다."""
    pass
