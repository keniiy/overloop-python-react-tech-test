from typing import List, Optional, Dict, Any
from techtest.repositories.region_repository import RegionRepository


class RegionService:
    """Service layer for Region business logic"""
    
    def __init__(self, region_repository: RegionRepository):
        self.region_repository = region_repository
    
    def get_all_regions(self) -> List[Dict[str, Any]]:
        """Get all regions as dictionaries"""
        regions = self.region_repository.get_all()
        return [region.asdict() for region in regions]
    
    def get_region_by_id(self, region_id: int) -> Optional[Dict[str, Any]]:
        """Get region by ID"""
        region = self.region_repository.get_by_id(region_id)
        return region.asdict() if region else None
    
    def get_region_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get region by code"""
        region = self.region_repository.get_by_code(code)
        return region.asdict() if region else None
    
    def create_region(self, region_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new region with validation"""
        code = region_data.get('code', '').strip().upper()
        name = region_data.get('name', '').strip()
        
        # Validate data
        errors = self.region_repository.validate_region_data(code, name)
        if errors:
            raise ValueError(f"Validation failed: {'; '.join(errors)}")
        
        # Create region
        region = self.region_repository.create(
            code=code,
            name=name
        )
        
        return region.asdict()
    
    def update_region(self, region_id: int, region_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing region"""
        if not self.region_repository.exists(region_id):
            return None
        
        code = region_data.get('code', '').strip().upper()
        name = region_data.get('name', '').strip()
        
        # For updates, we need to skip code uniqueness check if it's the same region
        existing_region = self.region_repository.get_by_id(region_id)
        if existing_region and existing_region.code != code:
            # Check if new code already exists
            if self.region_repository.get_by_code(code):
                raise ValueError(f"Region code '{code}' already exists")
        
        # Basic validation (without uniqueness check)
        errors = []
        if not code or len(code) != 2 or not code.isalpha():
            errors.append("Region code must be exactly 2 letters")
        if not name or len(name.strip()) < 2:
            errors.append("Region name must be at least 2 characters")
        
        if errors:
            raise ValueError(f"Validation failed: {'; '.join(errors)}")
        
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