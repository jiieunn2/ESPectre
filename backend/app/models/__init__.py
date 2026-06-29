"""모델 패키지. Base 와 모든 모델을 한곳에서 노출해 metadata 를 채운다.

Alembic env.py 가 `from app.models import Base` 만 해도 모든 테이블이
Base.metadata 에 등록되도록 여기서 모든 모델을 import 한다.
"""
from .base import Base
from .device import Device
from .floorplan import FloorPlan
from .reading import Reading
from .user import User, UserDevice

__all__ = ["Base", "Device", "FloorPlan", "Reading", "User", "UserDevice"]
