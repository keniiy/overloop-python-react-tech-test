from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class AuthorBase(BaseModel):
    """Base Author schema with common fields"""
    model_config = ConfigDict(str_strip_whitespace=True)

    first_name: str = Field(..., min_length=2, max_length=100, description="Author's first name")
    last_name: str = Field(..., min_length=2, max_length=100, description="Author's last name")


class CreateAuthorRequest(AuthorBase):
    """Schema for creating a new author"""
    pass


class UpdateAuthorRequest(AuthorBase):
    """Schema for updating an existing author"""
    pass


class AuthorResponse(AuthorBase):
    """Schema for author response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Author's unique identifier")
    full_name: str = Field(..., description="Author's full name")


class AuthorWithStatsResponse(AuthorResponse):
    """Schema for author response with article statistics"""
    article_count: int = Field(0, description="Number of articles written by this author")


class AuthorListResponse(BaseModel):
    """Schema for list of authors"""
    authors: List[AuthorResponse]
    total: int = Field(..., description="Total number of authors")
