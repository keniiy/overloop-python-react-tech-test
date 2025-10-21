from typing import List, Optional, Dict, Any, Tuple
from repositories.region_repository import RegionRepository
from schemas.region_schemas import CreateRegionRequest, UpdateRegionRequest


class RegionService:
    """Service layer for Region business logic"""
    
    def __init__(self, region_repository: RegionRepository):
        self.region_repository = region_repository
    
    def get_all_regions(self) -> List[Dict[str, Any]]:
        """Get all regions as dictionaries"""
        regions = self.region_repository.get_all()
        return [region.asdict() for region in regions]
    
    def get_all_regions_paginated(self, offset: int = 0, limit: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        """Get all regions with pagination"""
        regions, total = self.region_repository.get_all_paginated(offset, limit)
        region_data = [region.asdict() for region in regions]
        return region_data, total
    
    def get_region_by_id(self, region_id: int) -> Optional[Dict[str, Any]]:
        """Get region by ID"""
        region = self.region_repository.get_by_id(region_id)
        return region.asdict() if region else None
    
    def get_region_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get region by code"""
        region = self.region_repository.get_by_code(code)
        return region.asdict() if region else None
    
    def create_region(self, region_request: CreateRegionRequest) -> Dict[str, Any]:
        """Create new region with validation"""
        code = region_request.code
        name = region_request.name

        if self.region_repository.get_by_code(code):
            raise ValueError(f"Region code '{code}' already exists")
        
        # Create region
        region = self.region_repository.create(
            code=code,
            name=name
        )
        
        return region.asdict()
    
    def update_region(self, region_id: int, region_request: UpdateRegionRequest) -> Optional[Dict[str, Any]]:
        """Update existing region"""
        if not self.region_repository.exists(region_id):
            return None
        
        code = region_request.code
        name = region_request.name
        
        # For updates, we need to skip code uniqueness check if it's the same region
        existing_region = self.region_repository.get_by_id(region_id)
        if existing_region and existing_region.code != code:
            # Check if new code already exists
            if self.region_repository.get_by_code(code):
                raise ValueError(f"Region code '{code}' already exists")
        
        # Update region
        region = self.region_repository.update(
            region_id,
            code=code,
            name=name
        )
        
        return region.asdict() if region else None
    
    def delete_region(self, region_id: int) -> bool:
        """Delete region"""
        return self.region_repository.delete(region_id)
    
    def search_regions(self, search_term: str) -> List[Dict[str, Any]]:
        """Search regions by name"""
        if not search_term or not search_term.strip():
            return self.get_all_regions()
        
        regions = self.region_repository.search_by_name(search_term.strip())
        return [region.asdict() for region in regions]
    
    def search_regions_paginated(self, search_term: str, offset: int = 0, limit: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        """Search regions with pagination"""
        if not search_term or not search_term.strip():
            return self.get_all_regions_paginated(offset, limit)
        
        regions, total = self.region_repository.search_paginated(search_term.strip(), offset, limit)
        region_data = [region.asdict() for region in regions]
        return region_data, total
