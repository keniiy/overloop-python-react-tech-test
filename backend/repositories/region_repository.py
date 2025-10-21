from typing import List, Optional
from sqlalchemy.orm import Session

from models.region import Region
from repositories.base import BaseRepository


class RegionRepository(BaseRepository):
    """Repository for Region entity"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Region)
    
    def get_by_code(self, code: str) -> Optional[Region]:
        """Get region by code"""
        return self.db_session.query(Region).filter(
            Region.code == code.upper()
        ).first()
    
    def search_by_name(self, name: str) -> List[Region]:
        """Search regions by name"""
        search_pattern = f"%{name}%"
        return self.db_session.query(Region).filter(
            Region.name.ilike(search_pattern)
        ).all()
    
    def validate_region_data(self, code: str, name: str) -> List[str]:
        """Validate region data and return list of errors"""
        errors = []
        
        if not code or not code.strip():
            errors.append("Region code is required")
        elif len(code.strip()) != 2:
            errors.append("Region code must be exactly 2 characters")
        elif not code.strip().isalpha():
            errors.append("Region code must contain only letters")
        else:
            # Check if code already exists (for create operations)
            existing = self.get_by_code(code.strip())
            if existing:
                errors.append(f"Region code '{code.upper()}' already exists")
        
        if not name or not name.strip():
            errors.append("Region name is required")
        elif len(name.strip()) < 2:
            errors.append("Region name must be at least 2 characters")
        elif len(name.strip()) > 200:
            errors.append("Region name must be less than 200 characters")
        
        return errors