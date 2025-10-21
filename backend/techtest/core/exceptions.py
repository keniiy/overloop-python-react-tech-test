from typing import Optional, Dict, Any


class TechTestException(Exception):
    """Base exception for the techtest application"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ValidationError(TechTestException):
    """Raised when data validation fails"""
    pass


class NotFoundError(TechTestException):
    """Raised when a requested resource is not found"""
    pass


class ConflictError(TechTestException):
    """Raised when there's a conflict with existing data"""
    pass


class DatabaseError(TechTestException):
    """Raised when database operations fail"""
    pass


class AuthorHasArticlesError(ConflictError):
    """Raised when trying to delete an author who has written articles"""
    
    def __init__(self, author_id: int, article_count: int):
        message = f"Cannot delete author {author_id}: author has {article_count} articles"
        details = {"author_id": author_id, "article_count": article_count}
        super().__init__(message, details)


class RegionCodeExistsError(ConflictError):
    """Raised when trying to create a region with an existing code"""
    
    def __init__(self, code: str):
        message = f"Region code '{code}' already exists"
        details = {"code": code}
        super().__init__(message, details)