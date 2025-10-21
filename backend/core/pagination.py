from typing import Dict, Any, List, Optional
from flask import request
from pydantic import BaseModel, Field, validator
from math import ceil


class PaginationParams(BaseModel):
    """Pagination parameters with validation"""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be at least 1')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1:
            raise ValueError('Limit must be at least 1')
        if v > 100:
            raise ValueError('Limit cannot exceed 100')
        return v
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and limit"""
        return (self.page - 1) * self.limit


class SearchParams(BaseModel):
    """Search parameters with validation"""
    search: Optional[str] = Field(default=None, max_length=100, description="Search term")
    
    @validator('search', pre=True)
    def validate_search(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v


class PaginatedResponse(BaseModel):
    """Standard paginated response format"""
    data: List[Any]
    pagination: Dict[str, Any]
    
    @classmethod
    def create(
        cls, 
        data: List[Any], 
        total: int, 
        page: int, 
        limit: int,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a paginated response"""
        total_pages = ceil(total / limit) if limit > 0 else 1
        
        pagination_info = {
            'current_page': page,
            'per_page': limit,
            'total_items': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'next_page': page + 1 if page < total_pages else None,
            'prev_page': page - 1 if page > 1 else None
        }
        
        if search:
            pagination_info['search'] = search
            
        return {
            'data': data,
            'pagination': pagination_info
        }


def get_pagination_params() -> PaginationParams:
    """Extract and validate pagination parameters from request"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    return PaginationParams(page=page, limit=limit)


def get_search_params() -> SearchParams:
    """Extract and validate search parameters from request"""
    search = request.args.get('search', None)
    
    return SearchParams(search=search)


def get_filter_params(*allowed_filters: str) -> Dict[str, Any]:
    """Extract allowed filter parameters from request"""
    filters = {}
    
    for filter_name in allowed_filters:
        value = request.args.get(filter_name)
        if value is not None:
            # Try to convert to int if it looks like an ID
            if filter_name.endswith('_id'):
                try:
                    filters[filter_name] = int(value)
                except ValueError:
                    continue
            else:
                filters[filter_name] = value
                
    return filters


# Pagination utilities for repositories
def paginate_query(query, pagination: PaginationParams):
    """Apply pagination to a SQLAlchemy query"""
    return query.offset(pagination.offset).limit(pagination.limit)


def get_total_count(query):
    """Get total count from a SQLAlchemy query"""
    return query.count()