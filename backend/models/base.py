from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from connector import BaseModel


class TimestampMixin:
    """Mixin to add timestamp fields to models"""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseEntityModel(BaseModel, TimestampMixin):
    """Base model with common fields for all entities"""
    __abstract__ = True
    
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )