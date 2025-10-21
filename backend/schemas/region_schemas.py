from pydantic import BaseModel, Field, ConfigDict, validator
from typing import List


class RegionBase(BaseModel):
    """Base Region schema with common fields"""
    model_config = ConfigDict(str_strip_whitespace=True)

    code: str = Field(..., min_length=2, max_length=2, description="Two-letter region code")
    name: str = Field(..., min_length=2, max_length=200, description="Region name")
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isalpha():
            raise ValueError('Region code must contain only letters')
        return v.upper()


class CreateRegionRequest(RegionBase):
    """Schema for creating a new region"""
    pass


class UpdateRegionRequest(RegionBase):
    """Schema for updating an existing region"""
    pass


class RegionResponse(RegionBase):
    """Schema for region response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Region's unique identifier")


class RegionListResponse(BaseModel):
    """Schema for list of regions"""
    regions: List[RegionResponse]
    total: int = Field(..., description="Total number of regions")
