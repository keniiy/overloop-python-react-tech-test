from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from .author_schemas import AuthorResponse
from .region_schemas import RegionResponse


class ArticleBase(BaseModel):
    """Base Article schema with common fields"""
    title: str = Field(..., min_length=5, max_length=500, description="Article title")
    content: str = Field(..., min_length=10, description="Article content")


class CreateArticleRequest(ArticleBase):
    """Schema for creating a new article"""
    author_id: Optional[int] = Field(None, description="ID of the article's author")
    region_ids: Optional[List[int]] = Field(default_factory=list, description="List of region IDs")


class UpdateArticleRequest(ArticleBase):
    """Schema for updating an existing article"""
    author_id: Optional[int] = Field(None, description="ID of the article's author")
    region_ids: Optional[List[int]] = Field(None, description="List of region IDs")


class ArticleResponse(ArticleBase):
    """Schema for article response with relationships"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Article's unique identifier")
    author_id: Optional[int] = Field(None, description="Author's ID")
    author: Optional[AuthorResponse] = Field(None, description="Article author information")
    regions: List[RegionResponse] = Field(default_factory=list, description="Article regions")


class ArticleListResponse(BaseModel):
    """Schema for list of articles"""
    articles: List[ArticleResponse]
    total: int = Field(..., description="Total number of articles")


class ArticleSearchRequest(BaseModel):
    """Schema for article search parameters"""
    search: Optional[str] = Field(None, description="Search term for title/content")
    author_id: Optional[int] = Field(None, description="Filter by author ID")
    region_id: Optional[int] = Field(None, description="Filter by region ID")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Number of results to return")
    offset: Optional[int] = Field(0, ge=0, description="Number of results to skip")