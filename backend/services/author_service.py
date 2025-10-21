from typing import List, Optional
from repositories.author_repository import AuthorRepository
from models.author import Author
from schemas.author_schemas import (
    CreateAuthorRequest,
    UpdateAuthorRequest, 
    AuthorResponse,
    AuthorWithStatsResponse
)
from core.logger import LoggerMixin, log_database_operation
from core.exceptions import NotFoundError, AuthorHasArticlesError


class AuthorService(LoggerMixin):
    """Service layer for Author business logic"""
    
    def __init__(self, author_repository: AuthorRepository):
        self.author_repository = author_repository
    
    def get_all_authors(self) -> List[AuthorResponse]:
        """Get all authors with proper typing"""
        authors = self.author_repository.get_all()
        return [AuthorResponse.model_validate(author) for author in authors]
    
    def get_author_by_id(self, author_id: int) -> Optional[AuthorResponse]:
        """Get author by ID with proper typing"""
        author = self.author_repository.get_by_id(author_id)
        return AuthorResponse.model_validate(author) if author else None
    
    def create_author(self, author_data: CreateAuthorRequest) -> AuthorResponse:
        """Create new author with validation"""
        self.logger.info(f"Creating author: {author_data.first_name} {author_data.last_name}")
        
        first_name = author_data.first_name.strip()
        last_name = author_data.last_name.strip()
        
        # Validate data
        errors = self.author_repository.validate_author_data(first_name, last_name)
        if errors:
            self.logger.warning(f"Author validation failed: {errors}")
            raise ValueError(f"Validation failed: {'; '.join(errors)}")
        
        # Create author
        author = self.author_repository.create(
            first_name=first_name,
            last_name=last_name
        )
        
        log_database_operation("CREATE", "author", author.id, {"name": f"{first_name} {last_name}"})
        self.logger.info(f"Successfully created author with ID: {author.id}")
        
        return AuthorResponse.model_validate(author)
    
    def update_author(self, author_id: int, author_data: UpdateAuthorRequest) -> Optional[AuthorResponse]:
        """Update existing author"""
        # Check if author exists
        if not self.author_repository.exists(author_id):
            return None
        
        first_name = author_data.first_name.strip()
        last_name = author_data.last_name.strip()
        
        # Validate data
        errors = self.author_repository.validate_author_data(first_name, last_name)
        if errors:
            raise ValueError(f"Validation failed: {'; '.join(errors)}")
        
        # Update author
        author = self.author_repository.update(
            author_id,
            first_name=first_name,
            last_name=last_name
        )
        
        return AuthorResponse.model_validate(author) if author else None
    
    def delete_author(self, author_id: int) -> bool:
        """Delete author if they have no articles"""
        author = self.author_repository.get_by_id(author_id)
        if not author:
            return False
        
        # Check if author has articles
        if hasattr(author, 'articles') and author.articles:
            raise ValueError("Cannot delete author who has written articles")
        
        return self.author_repository.delete(author_id)
    
    def search_authors(self, search_term: str) -> List[AuthorResponse]:
        """Search authors by name"""
        if not search_term or not search_term.strip():
            return self.get_all_authors()
        
        authors = self.author_repository.search(search_term.strip())
        return [AuthorResponse.model_validate(author) for author in authors]
    
    def get_authors_with_article_count(self) -> List[AuthorWithStatsResponse]:
        """Get all authors with their article count"""
        authors = self.author_repository.get_all()
        result = []
        
        for author in authors:
            author_data = AuthorResponse.model_validate(author).model_dump()
            author_data['article_count'] = len(author.articles) if hasattr(author, 'articles') and author.articles else 0
            result.append(AuthorWithStatsResponse.model_validate(author_data))
        
        return result