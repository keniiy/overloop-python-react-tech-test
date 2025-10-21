from marshmallow import Schema, fields


class PaginationMetaSchema(Schema):
    """Schema for pagination metadata"""
    current_page = fields.Int(required=True, description="Current page number")
    per_page = fields.Int(required=True, description="Items per page")
    total_items = fields.Int(required=True, description="Total number of items")
    total_pages = fields.Int(required=True, description="Total number of pages")
    has_next = fields.Bool(required=True, description="Whether there is a next page")
    has_prev = fields.Bool(required=True, description="Whether there is a previous page")
    next_page = fields.Int(allow_none=True, description="Next page number if available")
    prev_page = fields.Int(allow_none=True, description="Previous page number if available")
    search = fields.Str(allow_none=True, description="Search term if used")


class PaginationParamsSchema(Schema):
    """Schema for pagination query parameters"""
    page = fields.Int(
        missing=1, 
        validate=lambda x: x >= 1, 
        metadata={"description": "Page number (1-based)", "example": 1}
    )
    limit = fields.Int(
        missing=20, 
        validate=lambda x: 1 <= x <= 100, 
        metadata={"description": "Items per page (1-100)", "example": 20}
    )
    search = fields.Str(
        missing=None,
        validate=lambda x: len(x.strip()) > 0 if x else True,
        metadata={"description": "Search term", "example": "john"}
    )


class AuthorFilterParamsSchema(PaginationParamsSchema):
    """Schema for author filtering parameters"""
    pass


class ArticleFilterParamsSchema(PaginationParamsSchema):
    """Schema for article filtering parameters"""
    author_id = fields.Int(
        missing=None,
        validate=lambda x: x > 0,
        metadata={"description": "Filter by author ID", "example": 1}
    )
    region_id = fields.Int(
        missing=None,
        validate=lambda x: x > 0,
        metadata={"description": "Filter by region ID", "example": 1}
    )


class RegionFilterParamsSchema(PaginationParamsSchema):
    """Schema for region filtering parameters"""
    pass