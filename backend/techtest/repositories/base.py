from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session


class BaseRepository(ABC):
    """Abstract base repository with common CRUD operations"""
    
    def __init__(self, db_session: Session, model_class):
        self.db_session = db_session
        self.model_class = model_class
    
    def get_all(self) -> List[Any]:
        """Get all entities"""
        return self.db_session.query(self.model_class).all()
    
    def get_by_id(self, entity_id: int) -> Optional[Any]:
        """Get entity by ID"""
        return self.db_session.query(self.model_class).filter(
            self.model_class.id == entity_id
        ).first()
    
    def create(self, **kwargs) -> Any:
        """Create new entity"""
        entity = self.model_class(**kwargs)
        self.db_session.add(entity)
        self.db_session.flush()  # Get ID without committing
        return entity
    
    def update(self, entity_id: int, **kwargs) -> Optional[Any]:
        """Update existing entity"""
        entity = self.get_by_id(entity_id)
        if entity:
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            self.db_session.flush()
        return entity
    
    def delete(self, entity_id: int) -> bool:
        """Delete entity by ID"""
        entity = self.get_by_id(entity_id)
        if entity:
            self.db_session.delete(entity)
            self.db_session.flush()
            return True
        return False
    
    def exists(self, entity_id: int) -> bool:
        """Check if entity exists"""
        return self.db_session.query(self.model_class).filter(
            self.model_class.id == entity_id
        ).first() is not None
    
    def count(self) -> int:
        """Get total count of entities"""
        return self.db_session.query(self.model_class).count()